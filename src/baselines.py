"""Baselines on the TRAINING patients only (test patients stay locked).

Three detectors, each turned into an alarm with the same rule (src/metrics.py):
  1. motion only : log10 of 2-8 Hz movement power (chest sensor, neck if chest missing),
                   relative to the same person's previous hour
  2. heart only  : heart-rate rise vs the previous 2 minutes (beats/min)
  3. models      : logistic regression and small gradient-boosted trees, on motion features only
                   (phone) or motion + heart rate (watch). Scores are out-of-fold: 5-fold
                   cross-validation grouped by patient, so no patient is scored by a model trained on them.

For each detector we pick the threshold that gives <= N false alarms per 24 h, for several N.

    python src/baselines.py        ->  results/baselines_train_cv.csv
"""
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

from metrics import CFG, evaluate, seizure_table, threshold_for_fa

# Sensor scale differs by orders of magnitude between patients, so every motion level feature is
# expressed relative to the same person's median over the PREVIOUS hour (causal, works on a phone).
MOTION = ["rel_band", "rel_std", "rel_low", "rel_line", "rel_band_30s", "peak_ratio", "dom_freq",
          "tilt_change", "mot_missing"]
HEART = ["hr_rel", "hr_delta", "hr_missing"]
FEATURES = MOTION + HEART


def add_features(d):
    def pick(a, b):
        return d[a].where(d[a].notna(), d[b])
    eps = 1e-12
    d["log_band"] = np.log10(pick("chest_band_pow", "neck_band_pow") + eps)
    d["log_std"] = np.log10(pick("chest_std", "neck_std") + eps)
    d["log_low"] = np.log10(pick("chest_low_pow", "neck_low_pow") + eps)
    d["log_line"] = np.log10(pick("chest_line_len", "neck_line_len") + eps)
    d["peak_ratio"] = pick("chest_peak_ratio", "neck_peak_ratio")
    d["dom_freq"] = pick("chest_dom_freq", "neck_dom_freq")
    d["tilt"] = pick("chest_tilt", "neck_tilt")
    # context from the past only (the phone cannot see the future)
    g = d.groupby(["sub", "run"], sort=False)
    past_hour = lambda x: x.rolling(720, min_periods=12).median().shift(1)
    for src, dst in [("log_band", "rel_band"), ("log_std", "rel_std"), ("log_low", "rel_low"),
                     ("log_line", "rel_line"), ("hr", "hr_rel")]:
        d[dst] = d[src] - g[src].transform(past_hour)
    d["rel_band_30s"] = g["rel_band"].transform(lambda x: x.rolling(6, min_periods=1).mean())
    d["tilt_change"] = (d["tilt"] - g["tilt"].transform(lambda x: x.rolling(24, min_periods=1).median().shift(1))).abs()
    d["hr_missing"] = d["hr"].isna().astype(float)
    d["mot_missing"] = d["log_band"].isna().astype(float)
    return d


def fit_lr(train, feats=FEATURES):
    med = train[feats].median()
    X = train[feats].fillna(med).to_numpy()
    mu, sd = X.mean(0), X.std(0) + 1e-9
    m = LogisticRegression(class_weight="balanced", max_iter=500, C=1.0, random_state=CFG["seed"])
    keep = ~train["impd"].to_numpy()
    m.fit(((X - mu) / sd)[keep], train["label"].to_numpy()[keep])
    return {"feats": feats, "median": med, "mu": mu, "sd": sd, "model": m}


def score_lr(fit, d):
    X = d[fit["feats"]].fillna(fit["median"]).to_numpy()
    return fit["model"].decision_function((X - fit["mu"]) / fit["sd"])


def fit_tree(train, feats):
    """Small gradient-boosted trees (150 trees, depth 4). Non-seizure windows are subsampled to
    300k for speed; class_weight balances the rest. Small enough to export to JSON for the phone."""
    t = train[~train["impd"]]
    neg = t[t["label"] == 0]
    neg = neg.sample(n=min(len(neg), 300000), random_state=CFG["seed"])
    tt = pd.concat([t[t["label"] == 1], neg])
    m = HistGradientBoostingClassifier(max_depth=4, max_iter=150, learning_rate=0.1,
                                       class_weight="balanced", random_state=CFG["seed"])
    m.fit(tt[feats], tt["label"])
    return m


def main():
    split = json.load(open("configs/split.json"))
    cols = ["sub", "run", "t", "hr", "hr_delta", "label", "impd"] + \
           [f"{s}_{f}" for s in ["chest", "neck"]
            for f in ["band_pow", "std", "low_pow", "line_len", "peak_ratio", "dom_freq", "tilt"]]
    import glob
    files = [f for f in sorted(glob.glob("data/features_v2/*.csv")) if f.split("/")[-1][:7] in split["train"]]
    d = pd.concat([pd.read_csv(f, usecols=lambda c: c in cols).reindex(columns=cols) for f in files],
                  ignore_index=True)
    d["impd"] = d["impd"].astype(bool)
    d = add_features(d)
    d["hr_rise"] = d["hr_delta"]
    seizures = seizure_table(set(split["train"]))
    print(f"{d['sub'].nunique()} train patients, {len(seizures)} seizures, {len(d) * 5 / 3600:.0f} h")

    # out-of-fold logistic regression scores
    d["lr"] = np.nan
    d["lr_motion"] = np.nan
    for k, (tr, va) in enumerate(GroupKFold(n_splits=5).split(d, groups=d["sub"])):
        for col, feats in [("lr", FEATURES), ("lr_motion", MOTION)]:
            fit = fit_lr(d.iloc[tr], feats)
            d.loc[d.index[va], col] = score_lr(fit, d.iloc[va])
        for col, feats in [("tree", FEATURES), ("tree_motion", MOTION)]:
            m = fit_tree(d.iloc[tr], feats)
            d.loc[d.index[va], col] = m.predict_proba(d.iloc[va][feats])[:, 1]
        print("fold", k, "done", flush=True)

    rows = []
    detectors = {"motion power rule": "rel_band", "heart rate rise rule": "hr_rise",
                 "motion model (LR, phone)": "lr_motion", "motion + heart rate model (LR, watch)": "lr",
                 "motion model (trees, phone)": "tree_motion",
                 "motion + heart rate model (trees, watch)": "tree"}
    for name, col in detectors.items():
        lo, hi = np.nanpercentile(d[col], 50), np.nanmax(d[col])
        iters = 18 if col.startswith("tree") else 14
        for target in CFG["eval"]["target_fa_per_24h"]:
            thr, per_sz, s = threshold_for_fa(d, col, seizures, target, lo, hi, iters)
            row = {"detector": name, "target_fa_24h": target, "threshold": thr, **s}
            for label, mask in [("f2b", per_sz["sz_type"].str.contains("f2b")),
                                ("asleep", per_sz["vigilance"] == "asleep"),
                                ("awake", per_sz["vigilance"] == "awake")]:
                row[f"sens_{label}_pct"] = 100 * per_sz.loc[mask, "detected"].mean()
                row[f"n_{label}"] = int(mask.sum())
            rows.append(row)
            print(f"{name:38s} FA<= {target:>3}: sens {s['sensitivity_pct']:5.1f}%  "
                  f"f2b {row['sens_f2b_pct']:5.1f}%  FA/24h {s['fa_per_24h']:.2f}  "
                  f"latency {s['median_latency_s']:.0f} s", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv("results/baselines_train_cv.csv", index=False, float_format="%.3f")
    d[["sub", "run", "t", "label", "rel_band", "hr_rise", "lr", "lr_motion", "tree", "tree_motion"]].to_pickle("data/train_scores.pkl")


if __name__ == "__main__":
    main()
