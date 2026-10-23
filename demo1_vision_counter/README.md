# Demo 1 - The camera counts the room (~4 min on stage)

Phone camera -> hub -> MQTT `phone/frames` -> YOLOv8 pose on the laptop ->
live person count + raised-hand detection -> shared state for Demo 2.

Talk beat (Teknik Informatika): real-time computer vision and edge
analytics - a model small enough for a laptop, fast enough for live video.
Courses on the slide: Computer Vision, Deep Learning, Pengolahan Citra Digital.

## Run

1. Hub running, phone Camera toggle on, phone propped facing the audience.
2. `python demo1_vision_counter/main.py --show`  (first run downloads
   yolov8n-pose.pt, ~6 MB)
3. Ask the audience to raise their hands - watch the counters move.

## Notes

- `--show` opens an annotated preview window (this is what you screen-share).
- Counts are written atomically to `demo1_vision_counter/state.json` -
  that file is the contract with Demo 2's dashboard.
- Raised hand = either wrist keypoint above the nose keypoint. Crude, fast,
  and visibly correct from stage. Tune `HAND_MARGIN` for your venue.
- CPU is fine at 640px input; `--model yolov8s-pose.pt` if the laptop has a GPU.
