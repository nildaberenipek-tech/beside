# Beside Band: hardware roadmap

**Status: plan only. Not built, not tested.** The hackathon version of Beside uses only the
phone. This document describes the low-cost chest band we plan to build afterwards.

## Why a chest band

The detection model is trained on SeizeIT2, where the motion sensor and the single-lead ECG sat
on the **left chest** (and the back of the neck). A band worn on the chest sees almost the same
signals, so the trained model can be reused instead of collecting a new dataset first.
A phone on the mattress sees a damped version of the movement; a band also adds heart rate,
which in our training-set experiments doubled the share of all seizures detected and cut median
alarm latency from about 50 s to about 34 s (see `results/baselines_train_cv.csv`).

| Signal | How the band measures it | Matches SeizeIT2? |
|---|---|---|
| Movement (convulsions) | 3-axis accelerometer + gyroscope, 25 Hz | yes, chest accelerometer at 25 Hz |
| Heart rate | single-lead ECG from two chest electrodes | yes, single-lead chest ECG |
| Breathing | slow (0.1-0.5 Hz) chest-wall movement in the same accelerometer | not labelled in SeizeIT2; exploratory |

## Parts (approximate prices, late 2026)

| Part | Example | Role | ~ USD |
|---|---|---|---|
| Microcontroller with Bluetooth LE | ESP32-C3 or ESP32-S3 mini board | reads sensors, sends data to the phone | 4-8 |
| Motion sensor | MPU-6050 or LSM6DS3 (accelerometer + gyroscope) | movement, breathing | 2-4 |
| ECG front end | AD8232 module + 3 snap electrodes | heart rate | 4-6 |
| Battery | 3.7 V LiPo, 300-500 mAh, **with protection circuit** | power for one night | 4 |
| Charger | TP4056 module **with protection** | charging | 1 |
| Strap and case | elastic chest strap, 3D-printed or small plastic box | wearing | 3-5 |
| **Total** | | | **about 18-28** |

For comparison, the commercial devices named in the README cost several hundred dollars or need
a subscription.

## Safety rules (non-negotiable)

1. **Battery only while worn.** The ECG electrodes touch the skin; the band must never be worn
   while plugged into USB or a charger. The firmware refuses to stream ECG while USB power is detected.
2. Use only LiPo cells with a built-in protection circuit and a protected charger; never charge
   overnight while worn or unattended.
3. Smooth, closed case; no exposed solder or wires against the skin.
4. Any test on a person (even team members) only after ethics approval required by the
   competition we enter, with written consent.

## Data path and software integration

```
 Beside Band (ESP32)                      Phone (Beside web app)
 accelerometer 25 Hz ----+
 ECG 256 Hz -> R-peaks --+--> BLE packets --> Web Bluetooth --> same window features
                         |   (1 per second)                    same trees (model.json)
 battery level ----------+                                    same alarm rule + countdown
```

- The app gets a **sensor source** setting: `phone motion` (today) or `Beside Band`.
  Everything after the raw signal (10 s windows, per-person normalisation, the tree model,
  the alarm rule, the countdown, the messages) is shared, so the band adds no second detector.
- The band sends acceleration at 25 Hz (the SeizeIT2 rate) and beat times; the phone does the
  feature extraction, exactly as the Python pipeline does, so Python-JS parity tests cover both.
- **iPhone limitation:** Safari does not support Web Bluetooth. Options, in order:
  1. Android phones with Chrome (supported).
  2. On iPhone, a Web-Bluetooth-capable browser app (e.g. Bluefy).
  3. Later, a small native app.
- If the band disconnects or its battery is low, the app tells the user and the contacts
  ("monitoring stopped"), so silence is never mistaken for safety.

## Build plan

| Step | Work | Who |
|---|---|---|
| 1 | Breadboard: ESP32 + accelerometer, stream 25 Hz over BLE to a laptop | C++ teammate |
| 2 | Web Bluetooth page that plots the stream live | app teammate + assistant |
| 3 | Run the existing model on band data; check the per-person normalisation still works | assistant |
| 4 | Add AD8232 ECG; R-peak detection on the phone; compare with a pulse oximeter | team |
| 5 | Strap and case; battery life test (target: one full night) | team |
| 6 | Ethics approval, then home tests: false alarms per night in healthy volunteers | team + advisor |
| 7 | Only with a hospital partner: recordings from patients in an epilepsy monitoring unit | future |
