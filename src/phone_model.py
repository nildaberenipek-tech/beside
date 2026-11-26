"""Train the phone model on phone-identical motion features and export it to app/model.json.

Uses TRAINING patients only. Steps:
  1. 5-fold cross-validation grouped by patient -> out-of-fold scores -> thresholds that give
     at most 1, 2 and 4 false alarms per 24 h (and the metrics at each).
  2. Fit one final model on all training patients.
  3. Export trees + thresholds + filter coefficients to app/model.json for app/detector.js.

    python src/phone_model.py   ->  app/model.json, results/phone_model_train_cv.csv
"""
import glob
import json
import os

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold

import stream_features as SF
from metrics import CFG, seizure_table, threshold_for_fa

FEATURES = SF.FEATURES
TARGETS = {"fa_1_per_day": 1, "fa_2_per_day": 2, "fa_4_per_day": 4}


def load(split_name):
    split = json.load(open("configs/split.json"))
    subs = set(split[split_name])
    files = [f for f in sorted(glob.glob("data/features_stream/*.csv")) if os.path.basename(f)[:7] in subs]
    cols = ["sub", "run", "t", "label", "impd", "sz_type", "vigilance"] + FEATURES
    d = pd.concat([pd.read_csv(f, usecols=cols) for f in files], ignore_index=True)
    d["impd"] = d["impd"].astype(bool)
    return d, subs


def fit(train):
    t = train[~train["impd"]]
    neg = t[t["label"] == 0]
    neg = neg.sample(n=min(len(neg), 300000), random_state=CFG["seed"])
    tt = pd.concat([t[t["label"] == 1], neg])
    m = HistGradientBoostingClassifier(max_depth=4, max_iter=150, learning_rate=0.1,
                                       class_weight="balanced", random_state=CFG["seed"])
    m.fit(tt[FEATURES], tt["label"])
    return m


def export_trees(m):
    trees = []
    for (pred,) in m._predictors:
        nodes = []
        for nd in pred.nodes:
            nodes.append([int(nd["feature_idx"]), float(nd["num_threshold"]), int(nd["missing_go_to_left"]),
                          int(nd["left"]), int(nd["right"]), int(nd["is_leaf"]), float(nd["value"])])
        trees.append(nodes)
    return {"baseline": float(np.ravel(m._baseline_prediction)[0]), "trees": trees}


def score_trees(model, X):
    """Pure-numpy copy of the JavaScript tree walk (used by the parity test)."""
    raw = np.full(len(X), model["baseline"])
    for nodes in model["trees"]:
        for r in range(len(X)):
            i = 0
            while not nodes[i][5]:
                fi, thr, miss_left, l, rr = nodes[i][:5]
                v = X[r, fi]
                i = (l if miss_left else rr) if np.isnan(v) else (l if v <= thr else rr)
            raw[r] += nodes[i][6]
    return 1 / (1 + np.exp(-raw))


def main():
    d, subs = load("train")
    seizures = seizure_table(subs)
    print(f"{d['sub'].nunique()} train patients, {len(seizures)} seizures, {len(d) * 5 / 3600:.0f} h", flush=True)

    d["oof"] = np.nan
    for k, (tr, va) in enumerate(GroupKFold(n_splits=5).split(d, groups=d["sub"])):
        m = fit(d.iloc[tr])
        d.loc[d.index[va], "oof"] = m.predict_proba(d.iloc[va][FEATURES])[:, 1]
        print("fold", k, flush=True)

    rows, thresholds = [], {}
    for name, target in TARGETS.items():
        thr, per_sz, s = threshold_for_fa(d, "oof", seizures, target, 0.0, 1.0, iters=18)
        thresholds[name] = thr
        f2b = per_sz["sz_type"].str.contains("f2b")
        row = {"operating_point": name, "threshold": thr, **s,
               "sens_f2b_pct": 100 * per_sz.loc[f2b, "detected"].mean(), "n_f2b": int(f2b.sum()),
               "median_latency_f2b_s": per_sz.loc[f2b & per_sz["detected"], "latency_s"].median(),
               "sens_asleep_pct": 100 * per_sz.loc[per_sz["vigilance"] == "asleep", "detected"].mean(),
               "sens_awake_pct": 100 * per_sz.loc[per_sz["vigilance"] == "awake", "detected"].mean()}
        rows.append(row)
        print(f"{name}: thr {thr:.4f}  sens {s['sensitivity_pct']:.1f}%  f2b {row['sens_f2b_pct']:.1f}%  "
              f"FA/24h {s['fa_per_24h']:.2f}  f2b latency {row['median_latency_f2b_s']:.0f} s", flush=True)
    pd.DataFrame(rows).to_csv("results/phone_model_train_cv.csv", index=False, float_format="%.4f")

    final = fit(d)
    filters = {"fs": SF.FS, "win": SF.WIN, "step": SF.STEP, "warm": SF.WARM,
               "sos_band": SF.SOS_BAND.tolist(), "sos_low": SF.SOS_LOW.tolist()}
    model = {"name": "Beside phone motion model", "version": 1,
             "trained_on": f"SeizeIT2 training patients only ({d['sub'].nunique()} patients, seed {CFG['seed']})",
             "features": FEATURES, **export_trees(final), "filters": filters,
             "thresholds": {**thresholds, "default": thresholds["fa_2_per_day"],
                            "high_attention": thresholds["fa_4_per_day"]},
             "eval": {k: CFG["eval"][k] for k in ["persist_windows", "refractory_s"]}}
    json.dump(model, open("app/model.json", "w"), separators=(",", ":"))
    print("saved app/model.json", os.path.getsize("app/model.json") // 1024, "KB")
    # sanity: sklearn and our tree walk agree on a sample
    X = d[FEATURES].sample(2000, random_state=0).to_numpy()
    diff = np.abs(final.predict_proba(X)[:, 1] - score_trees(model, X)).max()
    print(f"sklearn vs exported trees: max diff {diff:.2e}")
    assert diff < 1e-9


if __name__ == "__main__":
    main()
