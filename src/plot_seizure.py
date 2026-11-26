"""Plot heart rate and body movement around one real seizure from SeizeIT2.

Usage:
    python src/plot_seizure.py --sub 031 --run 03 --onset 56454 --duration 78

Reads the ECG and motion EDF files from data/raw/ and saves a PNG to results/.
"""
import argparse
import os

import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pyedflib
from scipy.signal import butter, sosfiltfilt


def read_edf(path, start_s, length_s):
    """Read a time window [start_s, start_s + length_s] from every channel of an EDF file."""
    f = pyedflib.EdfReader(path)
    out = {}
    for i, label in enumerate(f.getSignalLabels()):
        fs = f.getSampleFrequency(i)
        out[label] = (f.readSignal(i, int(start_s * fs), int(length_s * fs)), fs)
    f.close()
    return out


def heart_rate(ecg, fs):
    """Detect R-peaks and return (time of each beat in s, heart rate in beats per minute)."""
    clean = nk.ecg_clean(ecg, sampling_rate=fs)
    _, info = nk.ecg_peaks(clean, sampling_rate=fs)
    peaks = info["ECG_R_Peaks"]
    rr = np.diff(peaks) / fs                     # seconds between beats
    bpm = 60.0 / rr
    t = peaks[1:] / fs
    ok = (bpm > 30) & (bpm < 220)                # drop physiologically impossible beats
    return t[ok], bpm[ok]


def motion_features(acc_xyz, fs, win_s=10, step_s=5):
    """Acceleration magnitude, plus 2-8 Hz band power in sliding windows (10 s, 50% overlap)."""
    mag = np.sqrt((acc_xyz ** 2).sum(axis=0))
    sos = butter(4, [2, 8], btype="band", fs=fs, output="sos")
    band = sosfiltfilt(sos, mag)
    win, step = int(win_s * fs), int(step_s * fs)
    centers, power = [], []
    for start in range(0, len(band) - win + 1, step):
        centers.append((start + win / 2) / fs)
        power.append(np.mean(band[start:start + win] ** 2))
    return mag, np.array(centers), np.array(power)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sub", default="031")
    p.add_argument("--run", default="03")
    p.add_argument("--onset", type=float, default=56454)
    p.add_argument("--duration", type=float, default=78)
    p.add_argument("--before", type=float, default=300, help="seconds shown before onset")
    p.add_argument("--after", type=float, default=300, help="seconds shown after the seizure ends")
    a = p.parse_args()

    stem = f"data/raw/sub-{a.sub}_ses-01_task-szMonitoring_run-{a.run}"
    start = a.onset - a.before
    length = a.before + a.duration + a.after

    ecg, fs_ecg = read_edf(stem + "_ecg.edf", start, length)["ECG SD"]
    mov = read_edf(stem + "_mov.edf", start, length)
    fs_mov = mov["ECGEMG SD ACC X"][1]
    acc = np.vstack([mov[f"ECGEMG SD ACC {ax}"][0] for ax in "XYZ"])   # chest sensor

    t_hr, bpm = heart_rate(ecg, fs_ecg)
    # motion corrupts single beats -> show a robust 15 s rolling median on top
    bpm_smooth = np.array([np.median(bpm[np.abs(t_hr - t) <= 7.5]) for t in t_hr])
    mag, t_pow, power = motion_features(acc, fs_mov)

    # x axis: minutes relative to seizure onset (0 = onset)
    to_min = lambda t: (t - a.before) / 60
    t_mag = np.arange(len(mag)) / fs_mov

    ink, line = "#1f2937", "#2563eb"
    fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
    panels = [
        (axes[0], to_min(t_hr), bpm, "Heart rate (beats/min) - grey: beat-to-beat, blue: 15 s median"),
        (axes[1], to_min(t_mag), mag, "Chest acceleration magnitude (sensor units)"),
        (axes[2], to_min(t_pow), power, "Movement power 2-8 Hz (10 s windows, 50% overlap)"),
    ]
    for ax, x, y, title in panels:
        ax.axvspan(0, a.duration / 60, color="#fde2e2", zorder=0)
        ax.plot(x, y, color=line if ax is not axes[0] else "#bfc7d5", lw=1.0 if ax is axes[0] else 1.2)
        ax.set_title(title, loc="left", fontsize=10, color=ink)
        ax.grid(axis="y", color="#e5e7eb", lw=0.8)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
    axes[0].plot(to_min(t_hr), bpm_smooth, color=line, lw=2)
    axes[0].text(a.duration / 120, axes[0].get_ylim()[1], "seizure", ha="center",
                 va="top", fontsize=9, color="#b91c1c")
    axes[-1].set_xlabel("Minutes from seizure onset (shaded = seizure, as labelled by clinicians)")
    fig.suptitle(f"SeizeIT2 sub-{a.sub} run-{a.run}: one focal-to-bilateral tonic-clonic seizure during sleep",
                 x=0.01, ha="left", fontsize=11, color=ink)
    fig.tight_layout()

    os.makedirs("results", exist_ok=True)
    out = f"results/seizure_sub-{a.sub}_run-{a.run}.png"
    fig.savefig(out, dpi=150)
    print("saved", out)

    # quick numbers for the README / explanation
    pre = bpm[(t_hr < a.before - 30)]
    pre = bpm_smooth[(t_hr < a.before - 30)]
    ictal = bpm_smooth[(t_hr >= a.before) & (t_hr <= a.before + a.duration + 60)]
    print(f"median HR 5 min before: {np.median(pre):.0f} bpm | peak smoothed HR during/just after seizure: {ictal.max():.0f} bpm")
    pre_p = power[t_pow < a.before - 10].mean()
    ict_p = power[(t_pow >= a.before) & (t_pow <= a.before + a.duration)].mean()
    print(f"movement power during seizure is {ict_p / pre_p:.0f}x the pre-seizure level")


if __name__ == "__main__":
    main()
