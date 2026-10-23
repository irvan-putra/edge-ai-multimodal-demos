"""
Demo 3 - low-latency sensor pipeline to a local hardware loop.

Subscribes to phone/sensors (JSON accelerometer events), detects shakes,
and fires a local "hardware" execution loop.

    python demo3_sensor_mqtt/main.py [--broker localhost]
"""
import argparse
import json
import math
import time

import paho.mqtt.client as mqtt

SHAKE_G = 2.2        # |acceleration| threshold, in g - tune for your phone
COOLDOWN_S = 0.75


def on_shake(magnitude: float):
    """The 'hardware execution loop'. Replace with something physical:

    - gpiozero:  LED(17).blink(n=3)            (Raspberry Pi)
    - pyserial:  ser.write(b'BUZZ\\n')          (Arduino)
    - boring but reliable: print + terminal bell
    """
    print(f"\a[{time.strftime('%H:%M:%S')}] SHAKE {magnitude:4.1f} g -> hardware loop fired")


def make_on_message():
    last = 0.0
    def on_message(client, userdata, msg):
        nonlocal last
        ev = json.loads(msg.payload)
        mag = math.sqrt(ev["x"] ** 2 + ev["y"] ** 2 + ev["z"] ** 2) / 9.81
        # scroll the raw stream - on stage this terminal IS the visual
        print(f"\r x={ev['x']:6.2f} y={ev['y']:6.2f} z={ev['z']:6.2f} | {mag:4.2f} g ", end="")
        if mag > SHAKE_G and time.time() - last > COOLDOWN_S:
            last = time.time()
            on_shake(mag)
    return on_message


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--broker", default="localhost",
                    help="local broker on show day; test.mosquitto.org only for rehearsal")
    args = ap.parse_args()

    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="demo3-sensors")
    c.on_message = make_on_message()
    c.connect(args.broker, 1883)
    c.subscribe("phone/sensors")
    print(f"subscribed to phone/sensors on {args.broker} - shake the phone")
    c.loop_forever()
