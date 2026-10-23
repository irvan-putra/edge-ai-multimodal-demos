# Demo 0 - Hands-free slide control (~2 min on stage)

Phone mic -> WebSocket -> hub -> MQTT `phone/audio` -> faster-whisper ->
"lajut/kembali" detection -> keystroke into the presentation.

Talk beat: zero-latency multimodal voice control on consumer hardware.
No cloud speech API, no API key, no internet.

## Run

1. `python hub/app.py`, open the hub URL on the phone, tap Microphone.
2. `python demo0_voice_slides/main.py` (first run downloads the whisper model).
3. Open the deck, click into the presentation window, then say
   **"Lanjut"** (next) / **"Kembali"** (back).

## Notes

- `--model small` is more accurate if the laptop has the headroom.
- Keystrokes use pynput: Right/Left arrows, which every slide tool understands.
  On macOS, grant the terminal Accessibility + Input Monitoring permission.
- Stage risk: venue noise. Hold the phone close, or use a lav mic as the
  laptop's default input and skip the phone entirely (set `SOURCE=local`).
