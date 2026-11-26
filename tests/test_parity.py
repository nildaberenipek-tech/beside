"""Python and JavaScript must compute the same features, scores and alarms.

    python tests/test_parity.py        (needs node and app/model.json)

A synthetic night (seeded): 75 min of quiet breathing with two turns in bed, then a 90 s
rhythmic 4 Hz convulsion, then quiet again. Both implementations process it sample by sample.
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
import stream_features as SF
from phone_model import score_trees

rng = np.random.default_rng(42)
fs = SF.FS
n = fs * 60 * 80
t = np.arange(n) / fs
g = np.array([0.2, 0.3, 9.7])[:, None] * np.ones(n)               # lying, gravity mostly on z
x = g + 0.01 * rng.standard_normal((3, n))
x[2] += 0.02 * np.sin(2 * np.pi * 0.25 * t)                       # breathing
for s in [20 * 60, 50 * 60]:                                      # turning over in bed
    i = slice(s * fs, (s + 8) * fs)
    x[:, i] += rng.standard_normal((3, 8 * fs)) * 0.8
    x[0, s * fs + 8 * fs:] += 1.5; x[2, s * fs + 8 * fs:] -= 0.3
s = 75 * 60                                                        # convulsion
i = slice(s * fs, (s + 90) * fs)
x[:, i] += 3 * np.sin(2 * np.pi * 4 * t[i]) * np.array([1, 0.6, 0.4])[:, None] + rng.standard_normal((3, 90 * fs))

model = json.load(open("app/model.json"))
base = pd.DataFrame(SF.base_features(x))
feats = SF.context_features(base)
py_p = score_trees(model, feats[model["features"]].to_numpy())

with tempfile.TemporaryDirectory() as tmp:
    sig = os.path.join(tmp, "sig.json")
    json.dump({"x": x[0].tolist(), "y": x[1].tolist(), "z": x[2].tolist()}, open(sig, "w"))
    subprocess.run(["node", "tests/parity_run.js", sig, "app/model.json"], check=True)
    js = pd.DataFrame(json.load(open(sig.replace(".json", "_js.json"))))

assert len(js) == len(base), (len(js), len(base))
worst = {}
for k in SF.BASE:
    worst["b_" + k] = np.nanmax(np.abs(js["b_" + k].to_numpy(float) - base[k].to_numpy(float)))
for k in SF.FEATURES:
    a, b = js[k].to_numpy(float), feats[k].to_numpy(float)
    assert (np.isnan(a) == np.isnan(b)).all(), f"NaN pattern differs in {k}"
    worst[k] = np.nanmax(np.abs(a - b))
worst["probability"] = np.max(np.abs(js["p"].to_numpy() - py_p))
for k, v in worst.items():
    print(f"{k:14s} max |JS - Python| = {v:.2e}")
assert max(worst.values()) < 1e-6, "parity failed"
thr = model["thresholds"]["default"]
print("windows:", len(js), "| JS alarms at", js.loc[js["alarm"], "t"].tolist(),
      "s | max p during convulsion", round(float(js.loc[(js.t > s) & (js.t < s + 100), "p"].max()), 3),
      "| max p elsewhere", round(float(js.loc[(js.t < s) | (js.t > s + 200), "p"].max()), 3), "| threshold", round(thr, 3))
print("PARITY OK")
