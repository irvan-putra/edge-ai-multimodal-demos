# Demo 2 - Raised hands become a live dashboard (~3 min on stage)

Demo 1's counts -> state.json -> this Streamlit polling/BI dashboard,
refreshing live in front of the room.

Talk beat (Sistem Informasi): from raw detections to decisions - an edge
analytics pipeline feeding a business-intelligence view in real time.
Courses on the slide: Analisis Big Data, Visualisasi Data, Kecerdasan Bisnis.

## Run

1. Demo 1 running (it writes `demo1_vision_counter/state.json`).
2. `streamlit run demo2_dashboard/app.py`
3. Full-screen the browser. Run a real vote: "Hands up if you've trained a
   model" - the charts become the source of truth for the room.

## Notes

- Polls state.json once a second; keeps a rolling history in memory.
- The "vote" toggle snapshots the current hands-up count as a vote option -
  use it to run two or three quick audience polls back to back.
- Stage risk is low (no model here) - if Demo 1 dies, its state.json just
  stops updating and the dashboard shows the last known counts. Narrate on.
