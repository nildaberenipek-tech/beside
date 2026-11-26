"""Parity on a real recording (optional: downloads ~37 MB from OpenNeuro).

    python tests/test_parity_real.py --sub 046 --run 01

Runs the full night through src/stream_features.py (Python) and app/detector.js (Node) and
compares every window's probability and alarms. Only TRAINING patients are allowed here,
so the locked test set is never looked at before the final evaluation.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
import stream_features as SF
from download_data import fetch, PREFIX
from extract_features import read_channels
from phone_model import score_trees

a = argparse.ArgumentParser()
a.add_argument("--sub", default="046")
a.add_argument("--run", default="01")
a = a.parse_args()
if f"sub-{a.sub}" not in json.load(open("configs/split.json"))["train"]:
    raise SystemExit(f"sub-{a.sub} is not a training patient; refusing to look at the locked test set.")
stem = f"sub-{a.sub}_ses-01_task-szMonitoring_run-{a.run}"
path = fetch(f"{PREFIX}sub-{a.sub}/ses-01/mov/{stem}_mov.edf", "data/raw")
labs = [f"ECGEMG SD ACC {x}" for x in "XYZ"]
ch = read_channels(path, labs)
acc = np.vstack([ch[l][0] for l in labs])

model = json.load(open("app/model.json"))
feats = SF.context_features(pd.DataFrame(SF.base_features(acc)))
py_p = score_trees(model, feats[model["features"]].to_numpy())
with tempfile.TemporaryDirectory() as tmp:
    sig = os.path.join(tmp, "sig.json")
    json.dump({"x": acc[0].tolist(), "y": acc[1].tolist(), "z": acc[2].tolist()}, open(sig, "w"))
    subprocess.run(["node", "tests/parity_run.js", sig, "app/model.json"], check=True)
    js = pd.DataFrame(json.load(open(sig.replace(".json", "_js.json"))))
dp = np.abs(js["p"].to_numpy() - py_p).max()
print(f"{len(js)} windows ({len(js) * 5 / 3600:.1f} h) | max |p_JS - p_Python| = {dp:.2e}")
ev = pd.read_csv(f"data/events/{stem}_events.tsv", sep="\t")
print("seizures:", ev[ev.eventType.str.startswith("sz")][["onset", "duration", "eventType"]].values.tolist())
print("JS alarms at (s):", js.loc[js["alarm"], "t"].tolist())
assert dp < 1e-9, "parity failed on real data"
print("REAL-DATA PARITY OK")
