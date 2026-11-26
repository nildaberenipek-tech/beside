"""Baselines on the TRAINING patients only (test patients stay locked).

Three detectors, each turned into an alarm with the same rule (src/metrics.py):
  1. motion only : log10 of 2-8 Hz movement power (chest sensor, neck if chest missing)
  2. heart only  : heart-rate rise vs the previous 2 minutes (beats/min)
  3. motion + HR : logistic regression on 8 features, scores are out-of-fold
                   (5-fold cross-validation grouped by patient, so no patient scores itself)

For each detector we pick the threshold that gives <= N false alarms per 24 h, for several N.

    python src/baselines.py        ->  results/baselines_train_cv.csv
"""
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

from metrics import CFG, evaluate, seizure_table, threshold_for_fa

FEATURES = ["log_band", "log_std", "log_low", "log_line", "hr", "hr_delta", "hr_missing", "mot_missing"]


def add_features(d):
    def pick(a, b):
        return d[a].where(d[a].notna(), d[b])
    eps = 1e-12
    d["log_band"] = np.log10(pick("chest_band_pow", "neck_band_pow") + eps)
    d["log_std"] = np.log10(pick("chest_std", "neck_std") + eps)
    d["log_low"] = np.log10(pick("chest_low_pow", "neck_low_pow") + eps)
    d["log_line"] = np.log10(pick("chest_line_len", "neck_line_len") + eps)
    d["hr_missing"] = d["hr"].isna().astype(float)
    d["mot_missing"] = d["log_band"].isna().astype(float)
    return d


def fit_lr(train):
    med = train[FEATURES].median()
    X = train[FEATURES].fillna(med).to_numpy()
    mu, sd = X.mean(0), X.std(0) + 1e-9
    m = LogisticRegression(class_weight="balanced", max_iter=500, C=1.0, random_state=CFG["seed"])
    keep = ~train["impd"].to_numpy()
    m.fit(((X - mu) / sd)[keep], train["label"].to_numpy()[keep])
    return {"median": med, "mu": mu, "sd": sd, "model": m}


def score_lr(fit, d):
    X = d[FEATURES].fillna(fit["median"]).to_numpy()
    return fit["model"].decision_function((X - fit["mu"]) / fit["sd"])


def main():
    split = json.load(open("configs/split.json"))
    cols = ["sub", "run", "t", "hr", "hr_delta", "label", "impd"] + \
           [f"{s}_{f}" for s in ["chest", "neck"] for f in ["band_pow", "std", "low_pow", "line_len"]]
    import glob
    files = [f for f in sorted(glob.glob("data/features/*.csv")) if f.split("/")[-1][:7] in split["train"]]
    d = pd.concat([pd.read_csv(f, usecols=lambda c: c in cols).reindex(columns=cols) for f in files],
                  ignore_index=True)
    d["impd"] = d["impd"].astype(bool)
    d = add_features(d)
    d["hr_rise"] = d["hr_delta"]
    seizures = seizure_table(set(split["train"]))
    print(f"{d['sub'].nunique()} train patients, {len(seizures)} seizures, {len(d) * 5 / 3600:.0f} h")

    # out-of-fold logistic regression scores
    d["lr"] = np.nan
    for k, (tr, va) in enumerate(GroupKFold(n_splits=5).split(d, groups=d["sub"])):
        fit = fit_lr(d.iloc[tr])
        d.loc[d.index[va], "lr"] = score_lr(fit, d.iloc[va])
        print("fold", k, "done", flush=True)

    rows = []
    detectors = {"motion only": "log_band", "heart rate only": "hr_rise", "motion + heart rate (LR)": "lr"}
    for name, col in detectors.items():
        lo, hi = np.nanpercentile(d[col], 50), np.nanmax(d[col])
        for target in CFG["eval"]["target_fa_per_24h"]:
            thr, per_sz, s = threshold_for_fa(d, col, seizures, target, lo, hi)
            row = {"detector": name, "target_fa_24h": target, "threshold": thr, **s}
            for label, mask in [("f2b", per_sz["sz_type"].str.contains("f2b")),
                                ("asleep", per_sz["vigilance"] == "asleep"),
                                ("awake", per_sz["vigilance"] == "awake")]:
                row[f"sens_{label}_pct"] = 100 * per_sz.loc[mask, "detected"].mean()
                row[f"n_{label}"] = int(mask.sum())
            rows.append(row)
            print(f"{name:28s} FA<= {target:>3}: sens {s['sensitivity_pct']:5.1f}%  "
                  f"f2b {row['sens_f2b_pct']:5.1f}%  FA/24h {s['fa_per_24h']:.2f}  "
                  f"latency {s['median_latency_s']:.0f} s", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv("results/baselines_train_cv.csv", index=False, float_format="%.3f")
    d[["sub", "run", "t", "label", "log_band", "hr_rise", "lr"]].to_pickle("data/train_scores.pkl")


if __name__ == "__main__":
    main()
