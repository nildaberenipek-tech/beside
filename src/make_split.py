"""Lock the patient-level train/test split ONCE, before any modelling.

Patients (not windows, not seizures) are split, so no test patient is ever seen in training.
Stratified by whether the patient had at least one focal-to-bilateral tonic-clonic (f2b)
seizure, because that is the seizure type the app is built for.

Usage: python src/make_split.py   ->  writes configs/split.json
"""
import glob
import json
import os
import random

import pandas as pd

cfg = json.load(open("configs/default.json"))

if os.path.exists("configs/split.json"):
    raise SystemExit("configs/split.json already exists. The test set is locked; delete it only on purpose.")

rows = []
for f in sorted(glob.glob("data/events/*_events.tsv")):
    d = pd.read_csv(f, sep="\t")
    d["sub"] = os.path.basename(f)[:7]
    rows.append(d)
ev = pd.concat(rows)
subs = sorted(ev["sub"].unique())
sz = ev[ev["eventType"].str.startswith("sz")]
f2b_subs = set(sz[sz["eventType"].str.contains("f2b|tonicClonic")]["sub"])

rng = random.Random(cfg["seed"])
test = []
for group in [sorted(s for s in subs if s in f2b_subs), sorted(s for s in subs if s not in f2b_subs)]:
    g = group[:]
    rng.shuffle(g)
    test += g[: round(len(g) * cfg["test_fraction"])]
train = [s for s in subs if s not in test]

split = {"seed": cfg["seed"], "train": sorted(train), "test": sorted(test)}
json.dump(split, open("configs/split.json", "w"), indent=1)
for name, ids in [("train", train), ("test", test)]:
    part = sz[sz["sub"].isin(ids)]
    print(f"{name}: {len(ids)} patients, {len(part)} seizures, "
          f"{part['eventType'].str.contains('f2b').sum()} f2b, {(part['vigilance'] == 'asleep').sum()} during sleep")
