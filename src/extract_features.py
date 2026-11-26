"""Turn raw SeizeIT2 recordings into one row per 10 s window (50% overlap).

For each run: download ECG + motion EDF, compute features, save a small CSV, delete the EDFs.

    python src/extract_features.py --split train          # all training patients
    python src/extract_features.py --sub 001 --run 01     # one run (for testing)

Output: data/features/sub-XXX_run-YY.csv
Columns: sub, run, t (window centre, s), features..., label (1 = window overlaps a seizure),
         sz_type, vigilance, plus 'valid_*' flags when a signal is missing.
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import warnings

import neurokit2 as nk
import numpy as np
import pandas as pd
import pyedflib
from scipy.signal import butter, sosfiltfilt

from download_data import PREFIX, fetch, list_keys

warnings.filterwarnings("ignore")
CFG = json.load(open("configs/default.json"))
WIN, STEP = CFG["window_s"], CFG["step_s"]
OUT = "data/features"


def read_channels(path, labels):
    """Read whole channels from an EDF file -> dict label: (signal, fs)."""
    f = pyedflib.EdfReader(path)
    names = f.getSignalLabels()
    out = {}
    for lab in labels:
        if lab in names:
            i = names.index(lab)
            out[lab] = (f.readSignal(i), f.getSampleFrequency(i))
    f.close()
    return out


def motion_window_features(acc, fs, n_win):
    """acc: 3 x N array of one accelerometer. Returns dict of arrays, one value per window."""
    mag = np.sqrt((acc ** 2).sum(axis=0))
    band = sosfiltfilt(butter(4, CFG["motion_band_hz"], btype="band", fs=fs, output="sos"), mag)
    low = sosfiltfilt(butter(4, [0.3, 2], btype="band", fs=fs, output="sos"), mag)
    w, s = int(WIN * fs), int(STEP * fs)
    feats = {k: np.full(n_win, np.nan) for k in ["mot_std", "mot_band_pow", "mot_low_pow", "mot_line_len"]}
    for i in range(n_win):
        a, b = i * s, i * s + w
        if b > len(mag):
            break
        seg = mag[a:b]
        feats["mot_std"][i] = seg.std()
        feats["mot_band_pow"][i] = np.mean(band[a:b] ** 2)
        feats["mot_low_pow"][i] = np.mean(low[a:b] ** 2)
        feats["mot_line_len"][i] = np.mean(np.abs(np.diff(seg)))
    return feats


def ecg_window_features(ecg, fs, n_win):
    """Heart rate per window from R-peaks, plus change vs the previous 2 minutes."""
    hr = np.full(n_win, np.nan)
    try:
        clean = nk.ecg_clean(ecg, sampling_rate=fs)
        _, info = nk.ecg_peaks(clean, sampling_rate=fs)
        peaks = np.asarray(info["ECG_R_Peaks"])
    except Exception:
        peaks = np.array([])
    if len(peaks) > 10:
        t = peaks[1:] / fs
        bpm = 60 * fs / np.diff(peaks)
        ok = (bpm > 30) & (bpm < 220)
        t, bpm = t[ok], bpm[ok]
        starts = np.arange(n_win) * STEP
        lo = np.searchsorted(t, starts)
        hi = np.searchsorted(t, starts + WIN)
        for i in range(n_win):
            if hi[i] - lo[i] >= 3:                      # need >= 3 beats in 10 s
                hr[i] = np.median(bpm[lo[i]:hi[i]])
    base = pd.Series(hr).rolling(24, min_periods=6).median().shift(1).to_numpy()   # previous 2 min
    return {"hr": hr, "hr_delta": hr - base}


def labels_for(events_path, n_win):
    ev = pd.read_csv(events_path, sep="\t")
    sz = ev[ev["eventType"].str.startswith("sz")]
    label = np.zeros(n_win, dtype=int)
    sz_type = np.array([""] * n_win, dtype=object)
    vig = np.array([""] * n_win, dtype=object)
    starts = np.arange(n_win) * STEP
    for _, r in sz.iterrows():
        hit = (starts < r["onset"] + r["duration"]) & (starts + WIN > r["onset"])
        label[hit] = 1
        sz_type[hit] = r["eventType"]
        vig[hit] = r["vigilance"]
    impd = ev[ev["eventType"] == "impd"]          # impedance checks: artefacts, excluded later
    excl = np.zeros(n_win, dtype=bool)
    for _, r in impd.iterrows():
        excl |= (starts < r["onset"] + r["duration"]) & (starts + WIN > r["onset"])
    return label, sz_type, vig, excl


def process_run(sub, run, keep_raw=False):
    out_path = f"{OUT}/sub-{sub}_run-{run}.csv"
    if os.path.exists(out_path):
        return out_path
    stem = f"sub-{sub}_ses-01_task-szMonitoring_run-{run}"
    events = f"data/events/{stem}_events.tsv"
    dur = pd.read_csv(events, sep="\t")["recordingDuration"].iloc[0]
    n_win = int((dur - WIN) // STEP) + 1
    raw_dir = f"data/raw/tmp_{sub}_{run}"
    feats = {}
    paths = []
    for mod in ["ecg", "mov"]:
        key = f"{PREFIX}sub-{sub}/ses-01/{mod}/{stem}_{mod}.edf"
        try:
            paths.append(fetch(key, raw_dir))
        except Exception:
            continue
        ch = read_channels(paths[-1], ["ECG SD"] if mod == "ecg" else
                           [f"ECGEMG SD ACC {a}" for a in "XYZ"] + [f"EEG SD ACC {a}" for a in "XYZ"])
        if mod == "ecg" and "ECG SD" in ch:
            feats.update(ecg_window_features(*ch["ECG SD"], n_win))
        if mod == "mov":
            for prefix, name in [("ECGEMG SD", "chest"), ("EEG SD", "neck")]:
                labs = [f"{prefix} ACC {a}" for a in "XYZ"]
                if all(l in ch for l in labs):
                    acc = np.vstack([ch[l][0] for l in labs])
                    f = motion_window_features(acc, ch[labs[0]][1], n_win)
                    feats.update({k.replace("mot_", f"{name}_"): v for k, v in f.items()})
    if not keep_raw:
        for p in paths:
            os.remove(p)
        if os.path.isdir(raw_dir):
            os.rmdir(raw_dir)
    label, sz_type, vig, excl = labels_for(events, n_win)
    df = pd.DataFrame({"sub": f"sub-{sub}", "run": run, "t": np.arange(n_win) * STEP + WIN / 2, **feats,
                       "label": label, "sz_type": sz_type, "vigilance": vig, "impd": excl})
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(out_path, index=False, float_format="%.6g")
    return out_path


def runs_of(subs):
    pat = re.compile(r"(sub-\d+)_ses-01_task-szMonitoring_run-(\d+)_events\.tsv")
    out = []
    for f in sorted(os.listdir("data/events")):
        m = pat.match(f)
        if m and m.group(1) in subs:
            out.append((m.group(1)[4:], m.group(2)))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--split", choices=["train", "test"])
    p.add_argument("--sub")
    p.add_argument("--run")
    p.add_argument("--workers", type=int, default=4)
    a = p.parse_args()
    list_keys()
    if a.sub:
        print(process_run(a.sub, a.run))
        return
    subs = set(json.load(open("configs/split.json"))[a.split])
    todo = runs_of(subs)
    print(f"{len(todo)} runs to process")
    done = 0
    with cf.ProcessPoolExecutor(a.workers) as ex:
        futs = {ex.submit(process_run, s, r): (s, r) for s, r in todo}
        for fu in cf.as_completed(futs):
            done += 1
            try:
                fu.result()
            except Exception as e:
                print("FAILED", futs[fu], repr(e)[:200], flush=True)
            if done % 25 == 0:
                print(f"{done}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
