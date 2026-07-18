import streamlit as st
from pathlib import Path
from streamlit_app.services.data_loader import load_sessions

def main():
    st.title("Counsellor Queue – Nigeria")

    base = Path(__file__).resolve().parents[2]
    sessions = load_sessions(base / "data" / "session_exports" / "sessions.json")

    track_filter = st.selectbox(
        "Track",
        options=["all", "ukvi", "pre_cas", "credibility"],
        index=0
    )

    filtered = [
        s for s in sessions
        if s.get("country") == "Nigeria"
        and (track_filter == "all" or s.get("track") == track_filter)
    ]

    st.write(f"Found {len(filtered)} Nigeria sessions.")

    for s in filtered:
        overall = s.get("overall_scores", {})
        ready = overall.get("ready", False)
        overall_avg = overall.get("overall_avg_5c", 0.0)
        total_risk = overall.get("total_risk_score", 0.0)

        status_label = "READY" if ready else "NOT READY"
        status_color = "green" if ready else "red"

        st.markdown(
            f"### Session {s.get('session_id')} – {s.get('track').upper()} "
            f"(<span style='color:{status_color};font-weight:bold;'>{status_label}</span>)",
            unsafe_allow_html=True,
        )
        st.write(f"Overall avg 5C: {overall_avg:.2f}, total risk score: {total_risk:.1f}")
        st.json(s)

if __name__ == "__main__":
    main()