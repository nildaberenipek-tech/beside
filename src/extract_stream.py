"""Extract phone-identical motion features (src/stream_features.py) for every run of a split.

    python src/extract_stream.py --split train
    python src/extract_stream.py --split test

Downloads only the motion EDF of each run, uses the chest accelerometer (neck if the chest one
is missing), saves data/features_stream/sub-XXX_run-YY.csv, deletes the EDF.
"""
import argparse
import concurrent.futures as cf
import json
import os
import warnings

import numpy as np
import pandas as pd

from download_data import PREFIX, fetch, list_keys
from extract_features import labels_for, read_channels, runs_of
import stream_features as SF

warnings.filterwarnings("ignore")
OUT = "data/features_stream"
MOV_KEYS = {k for k, _ in list_keys() if k.endswith("_mov.edf")}


def process_run(sub, run):
    out_path = f"{OUT}/sub-{sub}_run-{run}.csv"
    if os.path.exists(out_path):
        return out_path
    stem = f"sub-{sub}_ses-01_task-szMonitoring_run-{run}"
    key = f"{PREFIX}sub-{sub}/ses-01/mov/{stem}_mov.edf"
    if key not in MOV_KEYS:
        return "no motion file"          # some SeizeIT2 runs have no motion recording
    raw_dir = f"data/raw/stream_{sub}_{run}"
    path = fetch(key, raw_dir)
    labs = {p: [f"{p} ACC {a}" for a in "XYZ"] for p in ["ECGEMG SD", "EEG SD"]}
    ch = read_channels(path, labs["ECGEMG SD"] + labs["EEG SD"])
    os.remove(path)
    os.rmdir(raw_dir)
    sensor = "ECGEMG SD" if all(l in ch for l in labs["ECGEMG SD"]) else "EEG SD"
    if not all(l in ch for l in labs[sensor]):
        return None
    acc = np.vstack([ch[l][0] for l in labs[sensor]])
    assert ch[labs[sensor][0]][1] == SF.FS
    base = pd.DataFrame(SF.base_features(acc))
    feats = SF.context_features(base)
    n_win = len(base)
    label, sz_type, vig, excl = labels_for(f"data/events/{stem}_events.tsv", n_win)
    df = pd.DataFrame({"sub": f"sub-{sub}", "run": run, "t": np.arange(n_win) * 5 + 5,
                       "sensor": "chest" if sensor == "ECGEMG SD" else "neck"})
    df = pd.concat([df, base.add_prefix("b_"), feats], axis=1)
    df["label"], df["sz_type"], df["vigilance"], df["impd"] = label, sz_type, vig, excl
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(out_path, index=False, float_format="%.6g")
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--split", choices=["train", "test"])
    p.add_argument("--sub")
    p.add_argument("--run")
    p.add_argument("--workers", type=int, default=6)
    a = p.parse_args()
    list_keys()
    if a.sub:
        print(process_run(a.sub, a.run))
        return
    todo = runs_of(set(json.load(open("configs/split.json"))[a.split]))
    print(len(todo), "runs", flush=True)
    skipped = 0
    with cf.ProcessPoolExecutor(a.workers) as ex:
        futs = {ex.submit(process_run, s, r): (s, r) for s, r in todo}
        for k, fu in enumerate(cf.as_completed(futs), 1):
            try:
                if fu.result() == "no motion file":
                    skipped += 1
            except Exception as e:
                print("FAILED", futs[fu], repr(e)[:200], flush=True)
            if k % 50 == 0:
                print(f"{k}/{len(todo)}", flush=True)
    print(f"done; {skipped} runs skipped because SeizeIT2 has no motion file for them")


if __name__ == "__main__":
    main()
