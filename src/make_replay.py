"""Cut a piece of a real SeizeIT2 night into app/replay.json for the app's "Real recording" screen.

    python src/make_replay.py --sub 046 --run 01 --before 1200 --after 480

Until the final test has been run, use TRAINING patients only (the script refuses test patients
unless --allow-test is given after the final evaluation).

The app then runs the SAME detector (app/detector.js + app/model.json) live over these samples,
so what the viewer sees is the phone code itself, not a precomputed result.
Raw values are stored as integers (value * 1e5) to keep the file small.
"""
import argparse
import json

import numpy as np
import pandas as pd

from download_data import PREFIX, fetch
from extract_features import read_channels


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sub", default="046")
    p.add_argument("--run", default="01")
    p.add_argument("--allow-test", action="store_true", help="only after the final test has been run")
    p.add_argument("--before", type=int, default=1200, help="seconds before the first seizure")
    p.add_argument("--after", type=int, default=480, help="seconds after the seizure starts")
    a = p.parse_args()

    stem = f"sub-{a.sub}_ses-01_task-szMonitoring_run-{a.run}"
    split = json.load(open("configs/split.json"))
    group = "test" if f"sub-{a.sub}" in split["test"] else "train"
    if group == "test" and not a.allow_test:
        raise SystemExit(f"sub-{a.sub} is a locked test patient; use a training patient before the final test.")
    ev = pd.read_csv(f"data/events/{stem}_events.tsv", sep="\t")
    sz = ev[ev["eventType"].str.startswith("sz")]
    motor = sz[sz["eventType"].str.contains("f2b|tonicClonic")]
    first = (motor if len(motor) else sz).iloc[0]          # centre on the first tonic-clonic seizure
    start = int(max(0, first["onset"] - a.before))
    end = int(first["onset"] + a.after)

    path = fetch(f"{PREFIX}sub-{a.sub}/ses-01/mov/{stem}_mov.edf", "data/raw")
    labs = [f"ECGEMG SD ACC {x}" for x in "XYZ"]
    ch = read_channels(path, labs)
    fs = int(ch[labs[0]][1])
    acc = np.vstack([ch[l][0][start * fs:end * fs] for l in labs])

    shown = sz[(sz["onset"] < end) & (sz["onset"] + sz["duration"] > start)]
    out = {
        "source": f"SeizeIT2 (OpenNeuro ds005873, CC0) sub-{a.sub} run-{a.run}",
        "patient_group": group,
        "fs": fs, "start_s": start, "scale": 1e5,
        "seizures": [[float(r["onset"] - start), float(r["onset"] + r["duration"] - start), r["eventType"], r["vigilance"]]
                     for _, r in shown.iterrows()],
        "x": np.round(acc[0] * 1e5).astype(int).tolist(),
        "y": np.round(acc[1] * 1e5).astype(int).tolist(),
        "z": np.round(acc[2] * 1e5).astype(int).tolist(),
    }
    json.dump(out, open("app/replay.json", "w"), separators=(",", ":"))
    print(f"app/replay.json: {(end - start) / 60:.0f} min, {group} patient, seizures {out['seizures']}")


if __name__ == "__main__":
    main()
