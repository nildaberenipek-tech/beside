"""List the real seizures in one SeizeIT2 events.tsv file.

Usage: python src/list_seizures.py examples/sample_events.tsv
Written by: <your name>
"""
import sys

import pandas as pd


def list_seizures(path):
    """Return a table with only the seizure rows (eventType starts with "sz")."""
    events = pd.read_csv(path, sep="\t")          # .tsv = columns separated by TAB
    # TODO 1: keep only the rows whose eventType starts with "sz"
    #         hint: events["eventType"].str.startswith("sz")
    seizures = events[events["eventType"].str.startswith("sz")]
    return seizures


def describe(row):
    """Turn one seizure row into a readable sentence."""
    minutes = row["onset"] / 60
    # TODO 2: return a sentence like
    #         "at minute 940.9: sz_foc_f2b, 78 s, asleep"
    return f'at minute {minutes:.1f}: {row["eventType"]}, {row["duration"]} s, {row["vigilance"]}'


if __name__ == "__main__":
    path = sys.argv[1]
    seizures = list_seizures(path)
    print(len(seizures), "seizures found")
    for _, row in seizures.iterrows():
        print(describe(row))
        # TODO 3: if the seizure lasted longer than 300 s, also print "EMERGENCY: over 5 minutes"
        if row["duration"] > 300:
            print("EMERGENCY: over 5 minutes")
