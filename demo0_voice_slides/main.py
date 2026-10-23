"""
Demo 0 - voice-controlled slide navigation.

Subscribes to phone/audio (PCM16 chunks), transcribes with faster-whisper
running fully locally, and presses Right/Left arrow when it hears
"Lanjut" (next) / "Kembali" (back).

    python demo0_voice_slides/main.py [--model base] [--lang id]
"""
import argparse
import base64
import json
import time

import numpy as np
import paho.mqtt.client as mqtt
from pynput.keyboard import Controller, Key

# Rolling buffer: whisper likes 2-4 s of context; we re-transcribe a sliding
# window so a command is caught even if it spans chunk boundaries.
WINDOW_S = 3.0
COOLDOWN_S = 1.0          # one command per second max - avoids double-fires
TARGET_RATE = 16000       # what whisper expects

COMMANDS = {"lanjut": Key.right, "kembali": Key.left}

keyboard = Controller()
audio_buf = np.zeros(0, dtype=np.int16)
last_fire = 0.0


def resample(pcm: np.ndarray, src_rate: int) -> np.ndarray:
    """Cheap linear resample to 16 kHz - fine for keyword spotting."""
    if src_rate == TARGET_RATE:
        return pcm
    n_out = int(len(pcm) * TARGET_RATE / src_rate)
    return np.interp(np.linspace(0, len(pcm) - 1, n_out),
                     np.arange(len(pcm)), pcm).astype(np.int16)


def make_on_message(model, lang):
    def on_message(client, userdata, msg):
        global audio_buf, last_fire
        chunk = json.loads(msg.payload)
        pcm = np.frombuffer(base64.b64decode(chunk["data"]), dtype=np.int16)
        pcm = resample(pcm, chunk.get("rate", TARGET_RATE))
        audio_buf = np.concatenate([audio_buf, pcm])[-int(WINDOW_S * TARGET_RATE):]

        text = " ".join(seg.text for seg, _ in
                        model.transcribe(audio_buf.astype(np.float32) / 32768,
                                         language=lang, beam_size=1))
        text = text.lower().strip()
        if text:
            print(f"\rheard: {text[:70]:<70}", end="")

        for word, key in COMMANDS.items():
            if word in text and time.time() - last_fire > COOLDOWN_S:
                last_fire = time.time()
                keyboard.press(key); keyboard.release(key)
                print(f"\n>>> {word.upper()} -> slide {'next' if key == Key.right else 'back'}")
                audio_buf = np.zeros(0, dtype=np.int16)  # consume the command
                break
    return on_message


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="base", help="whisper size: tiny/base/small")
    ap.add_argument("--lang", default="id")
    ap.add_argument("--mqtt", default="localhost")
    args = ap.parse_args()

    from faster_whisper import WhisperModel
    print(f"loading faster-whisper '{args.model}' (downloads once)...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="demo0-voice")
    c.on_message = make_on_message(model, args.lang)
    c.connect(args.mqtt, 1883)
    c.subscribe("phone/audio")
    print("listening on phone/audio - say 'Lanjut' or 'Kembali'")
    c.loop_forever()
