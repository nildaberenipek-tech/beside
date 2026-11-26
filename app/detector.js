/* Beside seizure detector: runs in the browser (and in Node for the parity test).

   Mirrors src/stream_features.py step by step:
   phone acceleration -> resample to 25 Hz -> 10 s windows every 5 s -> 7 base features
   -> features relative to the same person's previous hour -> gradient-boosted trees
   (app/model.json) -> probability -> alarm after `persist` windows in a row above threshold.
*/
(function (root) {
  "use strict";

  const EPS = 1e-12;

  // ---------- signal helpers ----------
  function sosfiltZero(sos, x) {
    // forward-only biquad cascade, zero initial state, Direct Form II transposed (= scipy.signal.sosfilt)
    let y = Float64Array.from(x);
    for (const [b0, b1, b2, , a1, a2] of sos) {
      let z1 = 0, z2 = 0;
      const out = new Float64Array(y.length);
      for (let n = 0; n < y.length; n++) {
        const xn = y[n];
        const yn = b0 * xn + z1;
        z1 = b1 * xn - a1 * yn + z2;
        z2 = b2 * xn - a2 * yn;
        out[n] = yn;
      }
      y = out;
    }
    return y;
  }
  const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
  function median(a) {
    const s = Float64Array.from(a).sort();
    const m = s.length >> 1;
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }
  function medianOfPast(hist, n, minCount) {
    // median of the last n entries before the current one, skipping NaN
    const past = hist.slice(Math.max(0, hist.length - n)).filter(v => Number.isFinite(v));
    return past.length >= minCount ? median(past) : NaN;
  }

  // ---------- base features of one window (buffer = up to 10 s warm-up + the 10 s window) ----------
  function windowBase(bx, by, bz, cfg) {
    const W = cfg.win, len = bx.length;
    const mag = new Float64Array(len);
    for (let i = 0; i < len; i++) mag[i] = Math.sqrt(bx[i] * bx[i] + by[i] * by[i] + bz[i] * bz[i]);
    const band = sosfiltZero(cfg.sos_band, mag).subarray(len - W);
    const low = sosfiltZero(cfg.sos_low, mag).subarray(len - W);
    const seg = mag.subarray(len - W);
    const m = mean(seg);
    let v = 0, ll = 0, bp = 0, lp = 0;
    for (let i = 0; i < W; i++) {
      v += (seg[i] - m) ** 2; bp += band[i] ** 2; lp += low[i] ** 2;
      if (i) ll += Math.abs(seg[i] - seg[i - 1]);
    }
    const f = { std: Math.sqrt(v / W), band_pow: bp / W, low_pow: lp / W, line_len: ll / (W - 1) };

    // spectrum of the de-meaned, Hann-windowed magnitude (same as numpy rfft)
    const nb = (W >> 1) + 1, val = 1 / (W * (1 / cfg.fs));
    const spec = new Float64Array(nb), freqs = new Float64Array(nb);
    const x = new Float64Array(W);
    for (let i = 0; i < W; i++) x[i] = (seg[i] - m) * (0.5 - 0.5 * Math.cos((2 * Math.PI * i) / (W - 1)));
    for (let k = 0; k < nb; k++) {
      let re = 0, im = 0;
      for (let i = 0; i < W; i++) {
        const a = (-2 * Math.PI * k * i) / W;
        re += x[i] * Math.cos(a); im += x[i] * Math.sin(a);
      }
      spec[k] = re * re + im * im;
      freqs[k] = k * val;
    }
    let tot = 0, best = -1, bestK = -1;
    for (let k = 0; k < nb; k++) {
      if (freqs[k] >= 1 && freqs[k] <= 12) {
        tot += spec[k];
        if (spec[k] > best) { best = spec[k]; bestK = k; }
      }
    }
    if (tot > 0) {
      const f0 = freqs[bestK];
      let near = 0;
      for (let k = 0; k < nb; k++) if (freqs[k] >= 1 && freqs[k] <= 12 && Math.abs(freqs[k] - f0) <= 0.5) near += spec[k];
      f.peak_ratio = near / tot; f.dom_freq = f0;
    } else { f.peak_ratio = NaN; f.dom_freq = NaN; }

    const gx = mean(bx.subarray(len - W)), gy = mean(by.subarray(len - W)), gz = mean(bz.subarray(len - W));
    const n = Math.sqrt(gx * gx + gy * gy + gz * gz);
    f.tilt = n > 0 ? (Math.acos(Math.min(1, Math.max(-1, gz / n))) * 180) / Math.PI : NaN;
    return f;
  }

  // ---------- trees ----------
  function treeScore(model, feats) {
    let raw = model.baseline;
    for (const nodes of model.trees) {
      let i = 0;
      while (!nodes[i][5]) {                       // [feature, threshold, missingLeft, left, right, isLeaf, value]
        const [fi, thr, missLeft, l, r] = nodes[i];
        const xv = feats[fi];
        i = Number.isNaN(xv) ? (missLeft ? l : r) : (xv <= thr ? l : r);
      }
      raw += nodes[i][6];
    }
    return 1 / (1 + Math.exp(-raw));
  }

  // ---------- streaming detector ----------
  class Detector {
    constructor(model, opts = {}) {
      this.m = model;
      this.cfg = model.filters;
      this.threshold = opts.threshold ?? model.thresholds.default;
      this.persist = model.eval.persist_windows;
      this.refractory = model.eval.refractory_s;
      this.onWindow = opts.onWindow || (() => {});
      this.onAlarm = opts.onAlarm || (() => {});
      this.reset();
    }
    reset() {
      const cap = this.cfg.warm + this.cfg.win;
      this.buf = [new Float64Array(cap), new Float64Array(cap), new Float64Array(cap)];
      this.filled = 0;            // samples in buffer
      this.total = 0;             // samples seen since start (at 25 Hz)
      this.hist = { band_pow: [], std: [], low_pow: [], line_len: [], tilt: [], rel_band: [] };
      this.run = 0; this.lastAlarm = -Infinity; this.windows = 0;
      this.rs = null;             // resampler state
    }
    // raw phone sample (any rate, any unit) with timestamp in ms
    push(x, y, z, tMs) {
      const dt = 1000 / this.cfg.fs;
      if (!this.rs) { this.rs = { next: tMs, px: x, py: y, pz: z, pt: tMs }; }
      const s = this.rs;
      if (tMs - s.pt > 2000) { s.next = tMs; s.pt = tMs; s.px = x; s.py = y; s.pz = z; }  // gap: restart grid
      while (s.next <= tMs) {
        const w = tMs === s.pt ? 1 : (s.next - s.pt) / (tMs - s.pt);
        this.pushSample(s.px + w * (x - s.px), s.py + w * (y - s.py), s.pz + w * (z - s.pz));
        s.next += dt;
      }
      s.pt = tMs; s.px = x; s.py = y; s.pz = z;
    }
    // one sample already at 25 Hz
    pushSample(x, y, z) {
      const cap = this.buf[0].length;
      if (this.filled < cap) {
        this.buf[0][this.filled] = x; this.buf[1][this.filled] = y; this.buf[2][this.filled] = z; this.filled++;
      } else {
        for (const b of this.buf) b.copyWithin(0, 1);
        this.buf[0][cap - 1] = x; this.buf[1][cap - 1] = y; this.buf[2][cap - 1] = z;
      }
      this.total++;
      const { win, step } = this.cfg;
      if (this.total >= win && (this.total - win) % step === 0) this.window();
    }
    window() {
      const n = this.filled;
      const b = this.buf.map(a => a.subarray(0, n));
      const f = windowBase(b[0], b[1], b[2], this.cfg);
      const h = this.hist, out = {};
      for (const [src, dst] of [["band_pow", "rel_band"], ["std", "rel_std"], ["low_pow", "rel_low"], ["line_len", "rel_line"]]) {
        const lg = Math.log10(f[src] + EPS);
        out[dst] = lg - medianOfPast(h[src], 720, 12);
        h[src].push(lg); if (h[src].length > 720) h[src].shift();
      }
      out.peak_ratio = f.peak_ratio; out.dom_freq = f.dom_freq;
      out.tilt_change = Math.abs(f.tilt - medianOfPast(h.tilt, 24, 1));
      h.tilt.push(f.tilt); if (h.tilt.length > 24) h.tilt.shift();
      h.rel_band.push(out.rel_band); if (h.rel_band.length > 6) h.rel_band.shift();
      const last = h.rel_band.filter(Number.isFinite);
      out.rel_band_30s = last.length ? mean(last) : NaN;

      const vec = this.m.features.map(k => (k in out ? out[k] : 0));
      const p = treeScore(this.m, vec);
      const tEnd = (this.windows * this.cfg.step + this.cfg.win) / this.cfg.fs;   // seconds since start
      this.windows++;
      this.run = p >= this.threshold ? this.run + 1 : 0;
      let alarm = false;
      if (this.run >= this.persist && tEnd - this.lastAlarm >= this.refractory) {
        alarm = true; this.lastAlarm = tEnd;
      }
      this.onWindow({ t: tEnd, p, features: out, base: f, alarm });
      if (alarm) this.onAlarm({ t: tEnd, p });
    }
  }

  const api = { Detector, windowBase, treeScore, sosfiltZero };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.BesideDetector = api;
})(typeof window !== "undefined" ? window : globalThis);
