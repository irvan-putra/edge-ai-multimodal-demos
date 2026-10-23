# Edge AI & Multimodal Applications in Python - Live Demos

Companion code for the PythonID Jakarta October Meetup talk
(Universitas Budi Luhur, 31 Oct 2026).

One smartphone, one laptop, one local Wi-Fi network. No cloud, no API keys.
The phone is just a sensor: mic, camera, IMU. All inference runs on the laptop.

## Architecture

```
phone browser ──WebSocket──> hub (FastAPI) ──MQTT──> demo processes
  mic · camera · IMU          localhost:8000         0 voice · 1 vision · 2 dashboard · 3 hardware
```

The phone never installs an app - it opens `http://<laptop-ip>:8000` in its
browser. The hub republishes every stream onto local MQTT topics, which is
itself the point of Demo 3: the transport is the product.

| Topic           | Payload                        | Used by |
| --------------- | ------------------------------ | ------- |
| `phone/audio`   | PCM16 mono frames (base64)     | Demo 0  |
| `phone/frames`  | JPEG camera frames (base64)    | Demo 1  |
| `phone/sensors` | JSON accelerometer/gyro events | Demo 3  |

## The 12-minute demo block (talk run order)

| Time | Demo | Shows | Run |
| ---- | ---- | ----- | --- |
| 0:00-2:00 | Demo 0 - voice slide control | faster-whisper, zero-latency local ASR. Say "Lanjut" / "Kembali" | `python demo0_voice_slides/main.py` |
| 2:00-6:00 | Demo 1 - audience counter (TI) | YOLO pose: counts people, detects raised hands | `python demo1_vision_counter/main.py --show` |
| 6:00-9:00 | Demo 2 - live dashboard (SI) | counts stream into a Streamlit polling/BI dashboard | `streamlit run demo2_dashboard/app.py` |
| 9:00-12:00 | Demo 3 - sensor pipeline (SK) | MQTT topics trigger local hardware loops | `python demo3_sensor_mqtt/main.py` |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Local MQTT broker (offline-first: no internet needed on show day)
#   Ubuntu/Debian: sudo apt install mosquitto && sudo systemctl start mosquitto
#   macOS:         brew install mosquitto && brew services start mosquitto
#   Windows:       https://mosquitto.org/download  (or use WSL)

# Start the phone hub
python hub/app.py          # prints the URL to open on the phone
```

Both devices must be on the same Wi-Fi. If the venue isolates clients
(very common!), bring a travel router or use the laptop's hotspot - that is
the single most likely failure on show day. Test everything in airplane-mode
conditions: local network up, internet down.

First run downloads models automatically: faster-whisper `base` (~150 MB)
and YOLOv8n-pose (~6 MB). Do this at home, not at the venue.

Each demo folder has its own README with the talk beats it supports.

## Backup plan (appendix slides 20-21)

Record each demo working (`--show` windows + terminal) *before* the talk.
If a demo fails live, play the recording and keep narrating - the audience
came for the ideas.
