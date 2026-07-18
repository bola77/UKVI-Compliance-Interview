import streamlit as st
from pathlib import Path
from streamlit_app.services.data_loader import load_sessions

def main():
    st.title("Cohorts and Intakes (Demo)")
    base = Path(__file__).resolve().parents[2]
    sessions = load_sessions(base / "data" / "session_exports" / "sessions.json")

    st.write("Later this page will group sessions by intake, country, and university.")
    st.write("Current raw data:")
    st.json(sessions)

if __name__ == "__main__":
    main()