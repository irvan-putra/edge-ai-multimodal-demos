"""
Demo 2 - live polling & BI dashboard.

Reads Demo 1's state.json once a second and renders:
  - big live metrics (people / hands up)
  - a rolling time series
  - a simple vote mode for audience polls

    streamlit run demo2_dashboard/app.py
"""
import json
import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st

STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "demo1_vision_counter", "state.json")
REFRESH_S = 1
HISTORY = 120  # data points kept (~2 min at 1 Hz)

st.set_page_config(page_title="Live Audience Dashboard", layout="wide")
st.title("Live Audience Dashboard")
st.caption("Edge analytics - every number on this page was a person or a raised hand, seconds ago.")


def read_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"people": 0, "hands_up": 0, "updated_at": None}


if "history" not in st.session_state:
    st.session_state.history = []
if "votes" not in st.session_state:
    st.session_state.votes = {}

# --- vote controls: snapshot the current hands-up count as an option ---
with st.sidebar:
    st.header("Audience poll")
    option = st.text_input("Vote option", placeholder='e.g. "Trained a model before"')
    if st.button("Snapshot hands-up as votes") and option:
        st.session_state.votes[option] = read_state()["hands_up"]
    if st.button("Reset poll"):
        st.session_state.votes = {}

state = read_state()
st.session_state.history.append({
    "time": datetime.now().strftime("%H:%M:%S"),
    "people": state["people"],
    "hands_up": state["hands_up"],
})
st.session_state.history = st.session_state.history[-HISTORY:]

c1, c2, c3 = st.columns(3)
c1.metric("People in the room", state["people"])
c2.metric("Hands up right now", state["hands_up"])
c3.metric("Last update", time.strftime("%H:%M:%S", time.localtime(state["updated_at"]))
          if state["updated_at"] else "-")

df = pd.DataFrame(st.session_state.history).set_index("time")
st.line_chart(df)

if st.session_state.votes:
    st.subheader("Poll results")
    st.bar_chart(pd.Series(st.session_state.votes))

# Streamlit reruns top-to-bottom on each interaction; this sleep+rerun loop
# turns it into a 1 Hz live view.
time.sleep(REFRESH_S)
st.rerun()
