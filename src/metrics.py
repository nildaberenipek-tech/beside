"""Event-based evaluation: did an alarm fire during each seizure, and how many false alarms per day?

Definitions (fixed before looking at test data, see configs/default.json):
- A window is "positive" when its score >= threshold.
- An alarm fires after `persist` consecutive positive windows (the phone must not ring on one jolt).
  Alarm time = end of the last window needed.
- After an alarm, no new alarm for `refractory_s` seconds (the countdown is already running).
- A seizure is detected if an alarm fires between (onset - tol_before) and (end + tol_after).
- Every other alarm is a false alarm. Windows during impedance checks ('impd') never alarm.
- Latency = alarm time - seizure onset, for the first alarm of each detected seizure.
"""
import json

import numpy as np
import pandas as pd

CFG = json.load(open("configs/default.json"))
EV = CFG["eval"]


def seizure_table(subs):
    """One row per seizure for these patients, read from the label files."""
    import glob
    import os
    rows = []
    for f in glob.glob("data/events/*_events.tsv"):
        name = os.path.basename(f)
        sub, run = name[:7], name.split("_run-")[1][:2]
        if sub not in subs:
            continue
        ev = pd.read_csv(f, sep="\t")
        for _, r in ev[ev["eventType"].str.startswith("sz")].iterrows():
            rows.append({"sub": sub, "run": int(run), "onset": r["onset"], "end": r["onset"] + r["duration"],
                         "duration": r["duration"], "sz_type": r["eventType"], "vigilance": r["vigilance"]})
    return pd.DataFrame(rows)


def alarms_for_run(t, score, threshold, persist=None, refractory=None):
    """Return alarm times (s) for one recording."""
    persist = persist or EV["persist_windows"]
    refractory = refractory or EV["refractory_s"]
    pos = np.nan_to_num(score, nan=-np.inf) >= threshold
    # count consecutive positives
    idx = np.arange(len(pos))
    last_neg = np.maximum.accumulate(np.where(~pos, idx, -1))
    run_len = idx - last_neg
    candidates = t[run_len >= persist] + CFG["window_s"] / 2
    alarms, last = [], -np.inf
    for a in candidates:
        if a - last >= refractory:
            alarms.append(a)
            last = a
    return np.array(alarms)


def evaluate(df, score_col, threshold, seizures, persist=None):
    """df: window table (sub, run, t, impd, score_col). Returns (per-seizure table, summary dict)."""
    det_rows, n_fa, hours = [], 0, 0.0
    sz_by_run = {k: g for k, g in seizures.groupby(["sub", "run"])}
    for (sub, run), g in df.groupby(["sub", "run"], sort=False):
        score = g[score_col].to_numpy().copy()
        score[g["impd"].to_numpy()] = np.nan
        hours += np.isfinite(score).sum() * CFG["step_s"] / 3600
        alarms = alarms_for_run(g["t"].to_numpy(), score, threshold, persist)
        szs = sz_by_run.get((sub, int(run)))
        used = np.zeros(len(alarms), dtype=bool)
        if szs is not None:
            for _, s in szs.iterrows():
                hit = (alarms >= s["onset"] - EV["tol_before_s"]) & (alarms <= s["end"] + EV["tol_after_s"])
                used |= hit
                det_rows.append({**s.to_dict(), "detected": bool(hit.any()),
                                 "latency_s": float(alarms[hit][0] - s["onset"]) if hit.any() else np.nan})
        n_fa += int((~used).sum())
    per_sz = pd.DataFrame(det_rows)
    summary = {
        "sensitivity_pct": 100 * per_sz["detected"].mean() if len(per_sz) else np.nan,
        "fa_per_24h": 24 * n_fa / hours if hours else np.nan,
        "median_latency_s": float(per_sz["latency_s"].median()),
        "n_seizures": len(per_sz),
        "n_false_alarms": n_fa,
        "hours": hours,
    }
    return per_sz, summary


def threshold_for_fa(df, score_col, seizures, target_fa_per_24h, lo, hi, iters=14):
    """Bisection: the lowest threshold (most sensitive) whose false-alarm rate is <= target."""
    for _ in range(iters):
        mid = (lo + hi) / 2
        _, s = evaluate(df, score_col, mid, seizures)
        if s["fa_per_24h"] <= target_fa_per_24h:
            hi = mid
        else:
            lo = mid
    per_sz, s = evaluate(df, score_col, hi, seizures)
    return hi, per_sz, s
