import streamlit as st
from pathlib import Path
from streamlit_app.services.data_loader import load_sessions
from streamlit_app.services.metrics import compute_track_summary

def main():
    st.title("Overview")
    base = Path(__file__).resolve().parents[2]
    sessions = load_sessions(base / "data" / "session_exports" / "sessions.json")

    if not sessions:
        st.info("No sessions yet. Run the Gradio app and complete a mock interview.")
        return

    summary = compute_track_summary(sessions)
    st.subheader("Sessions by track")
    st.table(summary)

if __name__ == "__main__":
    main()
