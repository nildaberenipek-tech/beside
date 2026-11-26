"""THE locked final test. Run once.

    python src/final_test.py

Fixed before any test result was seen (see the git history of this file):
- Model: app/model.json exactly as shipped in the app (trained on training patients only).
- Operating points: thresholds chosen on training patients by cross-validation
  (<= 1, 2 and 4 false alarms per 24 h). The app uses the "<= 2" threshold.
- Baseline: the single-feature motion rule (2-8 Hz movement power relative to the same person's
  previous hour), its threshold also chosen on training patients for <= 2 false alarms per 24 h.
- Alarm rule and event matching: src/metrics.py and configs/default.json (unchanged).
- Metrics: sensitivity per seizure (%), false alarms per 24 h, detection latency (s),
  for all seizures, tonic-clonic (focal to bilateral), other motor, non-motor/unknown, asleep, awake.
- 95 % confidence intervals: bootstrap over test PATIENTS (2000 resamples, seed 42).
- Writes results/final_test.json, results/final_test.md, results/final_test_latency.png.
- Refuses to run a second time (results/final_test.json exists) unless --i-know-this-is-a-rerun,
  and any rerun must be reported in the README.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import stream_features as SF
from metrics import CFG, evaluate, seizure_table, threshold_for_fa
from phone_model import score_trees

OUT_JSON = "results/final_test.json"
PREFIX = "results/final_test"        # changed to results/dryrun_train for --dry-run-on-train


def load(split_name):
    subs = set(json.load(open("configs/split.json"))[split_name])
    files = [f for f in sorted(glob.glob("data/features_stream/*.csv")) if os.path.basename(f)[:7] in subs]
    cols = ["sub", "run", "t", "label", "impd"] + SF.FEATURES
    d = pd.concat([pd.read_csv(f, usecols=cols) for f in files], ignore_index=True)
    d["impd"] = d["impd"].astype(bool)
    return d, subs


def group_of(t):
    if "f2b" in t or "tonicClonic" in t:
        return "tonic-clonic"
    if "_m_" in t or t.endswith("_m"):
        return "other motor"
    return "non-motor or unknown"


def summarise(per_sz, fa_by_sub, hours_by_sub, subs, rng, n_boot=2000):
    """Point estimates and patient-level bootstrap CIs."""
    per_sz = per_sz.copy()
    per_sz["group"] = per_sz["sz_type"].map(group_of)
    subsets = {"all seizures": per_sz, **{g: per_sz[per_sz["group"] == g] for g in
               ["tonic-clonic", "other motor", "non-motor or unknown"]},
               "asleep": per_sz[per_sz["vigilance"] == "asleep"], "awake": per_sz[per_sz["vigilance"] == "awake"]}
    subs = sorted(subs)
    boot_idx = [rng.choice(len(subs), len(subs), replace=True) for _ in range(n_boot)]
    out = {}
    for name, df in subsets.items():
        by_sub = df.groupby("sub")["detected"].agg(["sum", "count"]).reindex(subs, fill_value=0)
        hit, n = by_sub["sum"].to_numpy(), by_sub["count"].to_numpy()
        sens = [100 * hit[b].sum() / n[b].sum() for b in boot_idx if n[b].sum() > 0]
        out[name] = {"n_seizures": int(n.sum()), "n_patients": int((n > 0).sum()), "detected": int(hit.sum()),
                     "sensitivity_pct": 100 * hit.sum() / n.sum() if n.sum() else None,
                     "sensitivity_ci95": [float(np.percentile(sens, 2.5)), float(np.percentile(sens, 97.5))] if sens else None,
                     "median_latency_s": float(df.loc[df["detected"], "latency_s"].median()) if df["detected"].any() else None}
    fa = np.array([fa_by_sub.get(s, 0) for s in subs]); hrs = np.array([hours_by_sub.get(s, 0.0) for s in subs])
    fab = [24 * fa[b].sum() / hrs[b].sum() for b in boot_idx]
    out["false_alarms"] = {"n": int(fa.sum()), "hours": float(hrs.sum()), "per_24h": 24 * fa.sum() / hrs.sum(),
                           "per_24h_ci95": [float(np.percentile(fab, 2.5)), float(np.percentile(fab, 97.5))]}
    return out


def per_patient(d, col, thr, seizures):
    """Run evaluate() per patient to get false alarms and hours per patient (for the bootstrap)."""
    rows, fa, hrs = [], {}, {}
    for sub, g in d.groupby("sub"):
        per, s = evaluate(g, col, thr, seizures[seizures["sub"] == sub])
        rows.append(per)
        fa[sub], hrs[sub] = s["n_false_alarms"], s["hours"]
    return pd.concat([r for r in rows if len(r)], ignore_index=True), fa, hrs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--i-know-this-is-a-rerun", action="store_true")
    ap.add_argument("--dry-run-on-train", action="store_true",
                    help="run the exact same code on TRAINING patients (in-sample) to check it works; never touches test")
    a = ap.parse_args()
    global PREFIX, OUT_JSON
    if a.dry_run_on_train:
        PREFIX, OUT_JSON = "results/dryrun_train", "results/dryrun_train.json"
    elif os.path.exists(OUT_JSON) and not a.i_know_this_is_a_rerun:
        raise SystemExit(f"{OUT_JSON} exists: the final test has already been run. Rerunning must be reported.")

    model = json.load(open("app/model.json"))
    # baseline threshold, chosen on TRAINING patients only
    train, train_subs = load("train")
    thr_rule, _, s_rule = threshold_for_fa(train, "rel_band", seizure_table(train_subs),
                                           2, 0.0, float(np.nanmax(train["rel_band"])), iters=18)
    print(f"baseline rule threshold (train, <=2 FA/24h): {thr_rule:.3f}  (train FA/24h {s_rule['fa_per_24h']:.2f})")
    del train

    test, test_subs = load("train" if a.dry_run_on_train else "test")
    seizures = seizure_table(test_subs)
    test["p"] = score_trees(model, test[model["features"]].to_numpy())
    print(f"TEST: {test['sub'].nunique()} patients with motion data, {len(test) * 5 / 3600:.0f} h", flush=True)

    rng = np.random.default_rng(CFG["seed"])
    results = {"model": model["name"], "trained_on": model["trained_on"], "test_patients_with_motion": int(test["sub"].nunique()),
               "seizures_in_test_set": int(len(seizures)), "operating_points": {}}
    for name, thr in [("app default (<= 2 FA/24h on train)", model["thresholds"]["fa_2_per_day"]),
                      ("<= 1 FA/24h on train", model["thresholds"]["fa_1_per_day"]),
                      ("<= 4 FA/24h on train", model["thresholds"]["fa_4_per_day"])]:
        per, fa, hrs = per_patient(test, "p", thr, seizures)
        results["operating_points"][name] = {"threshold": thr, **summarise(per, fa, hrs, test["sub"].unique(), rng)}
        if name.startswith("app default"):
            per.to_csv(PREFIX + "_per_seizure.csv", index=False)
    per, fa, hrs = per_patient(test, "rel_band", thr_rule, seizures)
    results["baseline_motion_rule"] = {"threshold": thr_rule, **summarise(per, fa, hrs, test["sub"].unique(), rng)}

    json.dump(results, open(OUT_JSON, "w"), indent=1)
    write_markdown(results)
    plot_latency()
    print(open(PREFIX + ".md").read())


def write_markdown(r):
    def row(label, m):
        s = m["sensitivity_pct"]
        ci = m["sensitivity_ci95"]
        lat = m["median_latency_s"]
        return (f"| {label} | {m['detected']}/{m['n_seizures']} ({m['n_patients']} patients) | "
                + (f"{s:.0f}% [{ci[0]:.0f}-{ci[1]:.0f}]" if s is not None else "-") + " | "
                + (f"{lat:.0f}" if lat is not None else "-") + " |")
    lines = ["# Final test (locked test patients, run once)", "",
             f"Model: {r['model']}, {r['trained_on']}.",
             f"Test patients with motion data: {r['test_patients_with_motion']}. 95 % CIs: bootstrap over patients.", ""]
    for name, m in list(r["operating_points"].items()) + [("baseline: motion power rule (<= 2 FA/24h on train)", r["baseline_motion_rule"])]:
        fa = m["false_alarms"]
        lines += [f"## {name}", "",
                  f"False alarms: {fa['n']} in {fa['hours']:.0f} h = **{fa['per_24h']:.2f} per 24 h** "
                  f"[{fa['per_24h_ci95'][0]:.2f}-{fa['per_24h_ci95'][1]:.2f}]", "",
                  "| Seizures | Detected | Sensitivity [95% CI] | Median latency (s) |", "|---|---|---|---|"]
        for k in ["tonic-clonic", "other motor", "non-motor or unknown", "all seizures", "asleep", "awake"]:
            lines.append(row(k, m[k]))
        lines.append("")
    open(PREFIX + ".md", "w").write("\n".join(lines))


def plot_latency():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    per = pd.read_csv(PREFIX + "_per_seizure.csv")
    per["group"] = per["sz_type"].map(group_of)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    order = ["tonic-clonic", "other motor", "non-motor or unknown"]
    for i, g in enumerate(order):
        x = per.loc[(per["group"] == g) & per["detected"], "latency_s"]
        ax.scatter(x, np.full(len(x), i) + np.random.default_rng(0).uniform(-0.15, 0.15, len(x)),
                   s=22, color="#2f7d74", alpha=0.8, edgecolor="white", linewidth=0.5)
        n, k = int((per["group"] == g).sum()), int(((per["group"] == g) & per["detected"]).sum())
        ax.text(1.0, i, f"  {k}/{n} detected", transform=ax.get_yaxis_transform(), va="center", fontsize=9, color="#1d2b2a")
    ax.set_yticks(range(3), order)
    ax.axvline(0, color="#5e706e", lw=1, ls="--")
    ax.set_xlabel("Alarm time after seizure onset (s), detected seizures only")
    ax.set_title("Final test, app default threshold", loc="left", fontsize=10)
    for s_ in ["top", "right"]:
        ax.spines[s_].set_visible(False)
    fig.tight_layout()
    fig.savefig(PREFIX + "_latency.png", dpi=150)


if __name__ == "__main__":
    main()
