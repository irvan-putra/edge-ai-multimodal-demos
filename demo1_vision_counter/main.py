"""
Demo 1 - real-time audience counting + raised-hand detection.

Decodes JPEG frames from MQTT phone/frames, runs YOLOv8 pose locally,
and publishes {"people": N, "hands_up": M} to state.json for Demo 2.

    python demo1_vision_counter/main.py --show
"""
import argparse
import base64
import json
import os
import tempfile
import time

import cv2
import numpy as np
import paho.mqtt.client as mqtt

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")
HAND_MARGIN = 15          # px: wrist must be this far above the nose
WRITE_EVERY = 0.5         # s between state.json updates

# COCO keypoint indices used for the raised-hand heuristic
NOSE, L_WRIST, R_WRIST = 0, 9, 10
state = {"people": 0, "hands_up": 0, "updated_at": None}


def write_state():
    state["updated_at"] = time.time()
    # atomic write so the dashboard never reads a half-written file
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(STATE_PATH))
    with os.fdopen(fd, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_PATH)


def analyse(model, frame, args):
    global state
    res = model(frame, imgsz=640, verbose=False)[0]
    people = hands = 0
    if res.keypoints is not None:
        for kpts in res.keypoints.xy:
            people += 1
            k = kpts.cpu().numpy()
            if len(k) > R_WRIST and k[NOSE][1] > 0:
                wrist_above = (k[L_WRIST][1] < k[NOSE][1] - HAND_MARGIN or
                               k[R_WRIST][1] < k[NOSE][1] - HAND_MARGIN)
                if wrist_above:
                    hands += 1
    state.update({"people": people, "hands_up": hands})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="yolov8n-pose.pt")
    ap.add_argument("--mqtt", default="localhost")
    ap.add_argument("--show", action="store_true", help="annotated preview window")
    args = ap.parse_args()

    from ultralytics import YOLO
    print(f"loading {args.model} (downloads once)...")
    model = YOLO(args.model)
    last_write = 0.0

    def on_message(client, userdata, msg):
        nonlocal last_write
        jpg = base64.b64decode(msg.payload)
        frame = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return
        res = analyse(model, frame, args)
        if time.time() - last_write > WRITE_EVERY:
            write_state(); last_write = time.time()
            print(f"\rpeople: {state['people']:>3}   hands up: {state['hands_up']:>3}",
                  end="")
        if args.show:
            cv2.imshow("Demo 1 - audience counter", res.plot())
            cv2.waitKey(1)

    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="demo1-vision")
    c.on_message = on_message
    c.connect(args.mqtt, 1883)
    c.subscribe("phone/frames")
    print("watching phone/frames - point the phone at the audience")
    c.loop_forever()


if __name__ == "__main__":
    main()
