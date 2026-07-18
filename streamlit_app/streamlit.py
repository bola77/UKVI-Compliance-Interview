# streamlit_app/app.py
import streamlit as st
from pathlib import Path
from services.data_loader import load_sessions

BASE = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="Advisors Academy UKVI Dashboard",
    page_icon="🎓",
    layout="wide",
)

st.title("Advisors Academy UKVI Simulator – Dashboards")
st.markdown(
    "This dashboard reads session exports from the Gradio simulator "
    "to show UKVI, Pre-CAS, and Credibility performance."
)

# Quick overview on the main page
sessions = load_sessions(BASE / "data" / "session_exports" / "sessions.json")
st.metric("Total sessions", len(sessions))
tracks = [s.get("track") for s in sessions]
st.write("Tracks seen:", sorted(set(tracks)) if tracks else "None yet.")
st.write("Use the pages in the sidebar for detailed views.")
