"""Motion features computed exactly as the phone computes them (app/detector.js).

Why a separate file: the phone sees the signal live and never sees the future, so every filter
here is causal (forward only) and every window uses only past samples. Training on features
computed this way means the model on the phone sees the same numbers it was trained on.
tests/test_parity.py checks that Python and JavaScript agree.

Input: 3-axis acceleration at 25 Hz (any unit: all level features are taken relative to the same
person's previous hour, so the unit cancels).
"""
import json

import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt

FS = 25                       # Hz, SeizeIT2 motion rate; the phone resamples to this
WIN, STEP = 250, 125          # 10 s windows, 5 s step (50 % overlap)
WARM = 250                    # 10 s of earlier signal to warm up the filters
SOS_BAND = butter(4, [2, 8], btype="band", fs=FS, output="sos")
SOS_LOW = butter(4, [0.3, 2], btype="band", fs=FS, output="sos")
HANN = np.hanning(WIN)
FREQS = np.fft.rfftfreq(WIN, 1 / FS)
IN_BAND = (FREQS >= 1) & (FREQS <= 12)
EPS = 1e-12
BASE = ["std", "band_pow", "low_pow", "line_len", "peak_ratio", "dom_freq", "tilt"]
FEATURES = ["rel_band", "rel_std", "rel_low", "rel_line", "rel_band_30s", "peak_ratio", "dom_freq",
            "tilt_change"]


def sosfilt_zero(sos, x):
    """Forward-only biquad cascade with zero initial state (Direct Form II transposed).
    scipy's sosfilt does exactly this; app/detector.js writes the same loop out by hand."""
    return sosfilt(sos, np.asarray(x, dtype=float))


def window_base(buf_xyz):
    """buf_xyz: 3 x (WARM + WIN) samples, the last WIN of which form the window.
    Returns the 7 base features of that window."""
    mag = np.sqrt((buf_xyz ** 2).sum(axis=0))
    band = sosfilt_zero(SOS_BAND, mag)[-WIN:]
    low = sosfilt_zero(SOS_LOW, mag)[-WIN:]
    seg = mag[-WIN:]
    f = {"std": seg.std(), "band_pow": np.mean(band ** 2), "low_pow": np.mean(low ** 2),
         "line_len": np.mean(np.abs(np.diff(seg)))}
    spec = np.abs(np.fft.rfft((seg - seg.mean()) * HANN)) ** 2
    sb = spec[IN_BAND]
    if sb.sum() > 0:
        k = int(np.argmax(sb))
        f0 = FREQS[IN_BAND][k]
        near = IN_BAND & (np.abs(FREQS - f0) <= 0.5)
        f["peak_ratio"], f["dom_freq"] = spec[near].sum() / sb.sum(), f0
    else:
        f["peak_ratio"], f["dom_freq"] = np.nan, np.nan
    g = buf_xyz[:, -WIN:].mean(axis=1)
    n = np.linalg.norm(g)
    f["tilt"] = np.degrees(np.arccos(np.clip(g[2] / n, -1, 1))) if n > 0 else np.nan
    return f


def base_features(acc_xyz):
    """All windows of a recording. Window i covers samples [i*STEP, i*STEP + WIN)."""
    n_win = (acc_xyz.shape[1] - WIN) // STEP + 1
    rows = []
    for i in range(n_win):
        a, b = i * STEP, i * STEP + WIN
        buf = acc_xyz[:, max(0, a - WARM):b]
        if not np.isfinite(buf).all():
            rows.append({k: np.nan for k in BASE})
            continue
        rows.append(window_base(buf))
    return rows


def context_features(base):
    """base: DataFrame of base features (one row per window, in time order).
    Model inputs use only the past: median of the previous 720 windows (1 hour, at least 12
    valid), previous 24 windows (2 min) for posture, and the last 6 windows (30 s) for smoothing.
    NaN values are skipped, as in the JavaScript version."""
    past = lambda x, n, m: x.rolling(n, min_periods=m).median().shift(1)
    out = pd.DataFrame(index=base.index)
    for src, dst in [("band_pow", "rel_band"), ("std", "rel_std"), ("low_pow", "rel_low"),
                     ("line_len", "rel_line")]:
        lg = np.log10(base[src] + EPS)
        out[dst] = lg - past(lg, 720, 12)
    out["rel_band_30s"] = out["rel_band"].rolling(6, min_periods=1).mean()
    out["peak_ratio"], out["dom_freq"] = base["peak_ratio"], base["dom_freq"]
    out["tilt_change"] = (base["tilt"] - past(base["tilt"], 24, 1)).abs()
    return out[FEATURES]


def export_filters(path):
    json.dump({"fs": FS, "win": WIN, "step": STEP, "warm": WARM,
               "sos_band": SOS_BAND.tolist(), "sos_low": SOS_LOW.tolist()}, open(path, "w"))
