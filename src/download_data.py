"""Download SeizeIT2 files from the public OpenNeuro S3 bucket (CC0 licence).

    python src/download_data.py --labels                 # all events.tsv + participants.tsv (~3 MB)
    python src/download_data.py --sub 031 --run 03       # ECG + motion of one run (~80 MB)

Files go to data/ (ignored by git).
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import urllib.parse
import urllib.request

BASE = "https://s3.amazonaws.com/openneuro.org"
PREFIX = "ds005873/"


def list_keys():
    """Return every (file path, size in bytes) in the dataset, cached in data/s3_index.json."""
    cache = "data/s3_index.json"
    if os.path.exists(cache):
        return json.load(open(cache))
    keys, token = [], None
    while True:
        url = f"{BASE}?list-type=2&prefix={PREFIX}"
        if token:
            url += "&continuation-token=" + urllib.parse.quote(token)
        xml = urllib.request.urlopen(url).read().decode()
        keys += [(k, int(s)) for k, s in re.findall(r"<Key>(.*?)</Key>.*?<Size>(\d+)</Size>", xml)]
        m = re.search(r"<NextContinuationToken>(.*?)</NextContinuationToken>", xml)
        if not m:
            break
        token = m.group(1)
    os.makedirs("data", exist_ok=True)
    json.dump(keys, open(cache, "w"))
    return keys


def fetch(key, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, os.path.basename(key))
    if not os.path.exists(path):
        # download to a temporary name first, so an interrupted download is never mistaken for a full file
        for attempt in range(4):
            try:
                urllib.request.urlretrieve(f"{BASE}/{key}", path + ".part")
                os.replace(path + ".part", path)
                break
            except Exception:
                if attempt == 3:
                    raise
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", action="store_true")
    p.add_argument("--sub")
    p.add_argument("--run")
    a = p.parse_args()

    if a.labels:
        events = [k for k, _ in list_keys() if k.endswith("_events.tsv")]
        with cf.ThreadPoolExecutor(16) as ex:
            list(ex.map(lambda k: fetch(k, "data/events"), events))
        for f in ["participants.tsv", "events.json", "README"]:
            fetch(PREFIX + f, "data")
        print(f"downloaded {len(events)} event files")

    if a.sub and a.run:
        for mod in ["ecg", "mov"]:
            for ext in ["edf", "json"]:
                key = f"{PREFIX}sub-{a.sub}/ses-01/{mod}/sub-{a.sub}_ses-01_task-szMonitoring_run-{a.run}_{mod}.{ext}"
                print("saved", fetch(key, "data/raw"))


if __name__ == "__main__":
    main()
