# App screens (for the UI teammate)

One page (`index.html`), each screen is a `<section>`; only one is visible at a time.
Everything is stored on the phone (`localStorage`); nothing is sent to a server.

| # | Screen id | Who uses it | What it shows / does |
|---|-----------|-------------|----------------------|
| 1 | `settings` | doctor + patient | "Your safety plan": seizure type, typical duration, code word, any number of contacts; editable any time |
| 3 | `home` | patient | big buttons: Sleep mode, I feel an aura, Log, Replay real seizure; status line |
| 4 | `sleep` | patient | "Monitoring..." + live motion level bar; dims the screen; keeps phone awake |
| 5 | `aura` | patient | "High-attention mode ON", contact notified "aura reported"; listens with lower threshold |
| 6 | `countdown` | patient | big "Are you OK?" + 30 s countdown + huge "I'm OK" button; vibrates |
| 7 | `alert` | contact | message preview with location link; opens `sms:` or `wa.me` link (demo number) |
| 8 | `log` | patient -> doctor | list: time, duration, heart rate, trigger notes; "share with doctor" |
| 9 | `replay` | jury / demo | plays a real held-out SeizeIT2 seizure from `replay.json`; shows the moment the alarm fires |

## Alarm rule (same logic as Python `model.json`)
1. Motion score above threshold for N windows -> **countdown** (screen 6).
2. No answer in 30 s -> **alert** to contacts (screen 7).
3. Event longer than the patient's typical duration -> message "longer than usual".
4. Longer than 5 min (300 s) -> **emergency** level (status epilepticus rule).

## Browser features (need https -> GitHub Pages)
- `DeviceMotionEvent` (on iPhone: `DeviceMotionEvent.requestPermission()` after a tap)
- Web Speech API (code word), Geolocation, `navigator.vibrate` (not on iPhone), Wake Lock
- **Demo mode** button simulates motion for judges who deny sensor permissions.
