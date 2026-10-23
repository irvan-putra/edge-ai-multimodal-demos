"""
Phone hub - the bridge between the phone's browser and the local demos.

Serves phone.html (mic + camera + IMU capture, zero installs on the phone)
and republishes every incoming WebSocket message onto local MQTT topics:

    phone/audio    PCM16 mono audio frames (base64)      -> Demo 0
    phone/frames   JPEG camera frames (base64)           -> Demo 1
    phone/sensors  JSON accelerometer/gyro events        -> Demo 3

Run:  python hub/app.py
Then open the printed URL on the phone (same Wi-Fi).
"""
import asyncio
import socket

import paho.mqtt.client as mqtt
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pathlib import Path

MQTT_HOST = "localhost"          # local broker = works with the internet unplugged
MQTT_PORT = 1883

app = FastAPI(title="phone-hub")
mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="phone-hub")
mq.connect(MQTT_HOST, MQTT_PORT)
mq.loop_start()

TOPICS = {"audio": "phone/audio", "frame": "phone/frames", "sensor": "phone/sensors"}


@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "phone.html")


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    """One WebSocket per phone. Messages are JSON: {"kind": ..., "data": ...}."""
    await websocket.accept()
    print("[hub] phone connected")
    try:
        while True:
            msg = await websocket.receive_json()
            topic = TOPICS.get(msg.get("kind"))
            if topic:
                # MQTT is fire-and-forget; QoS 0 keeps latency in the milliseconds.
                mq.publish(topic, msg["data"])
    except WebSocketDisconnect:
        print("[hub] phone disconnected")


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # no traffic actually sent
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    print(f"\n  Open on the phone:  http://{lan_ip()}:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
