import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
SESSIONS_PATH = BASE / "data" / "session_exports" / "sessions.json"

def make_demo_session(session_id: str, track: str, country: str = "Nigeria"):
    now = datetime.utcnow().isoformat() + "Z"
    # Very simple demo: three questions with fake scores and risk
    questions = [
        {
            "question_id": f"{track.upper()}_DEMO_Q1",
            "question_text": "Demo question 1",
            "theme": "funding",
            "sub_theme": "sponsor_income",
            "risk_tag": "funding_unclear",
            "track": track,
            "question_started_at": now,
            "answered_at": now,
            "late": False,
            "attempt_number": 1,
            "max_attempts": 3,
            "input_mode": "audio",
            "audio_path": "",
            "transcript": "Demo transcript about sponsor income",
            "scores": {
                "correctness": 0.6,
                "content": 0.5,
                "clarity": 0.6,
                "confidence": 0.6,
                "composure": 0.6,
                "risk_tags": ["funding_unclear"],
                "risk_score": 3,
            },
        },
        {
            "question_id": f"{track.upper()}_DEMO_Q2",
            "question_text": "Demo question 2",
            "theme": "why_uk",
            "sub_theme": "decision_process",
            "risk_tag": "genuine_student_doubt",
            "track": track,
            "question_started_at": now,
            "answered_at": now,
            "late": False,
            "attempt_number": 1,
            "max_attempts": 3,
            "input_mode": "audio",
            "audio_path": "",
            "transcript": "Demo transcript about why UK and Nigeria return plans",
            "scores": {
                "correctness": 0.7,
                "content": 0.6,
                "clarity": 0.6,
                "confidence": 0.6,
                "composure": 0.6,
                "risk_tags": ["genuine_student_doubt"],
                "risk_score": 2,
            },
        },
        {
            "question_id": f"{track.upper()}_DEMO_Q3",
            "question_text": "Demo question 3",
            "theme": "future_plans",
            "sub_theme": "career_in_nigeria",
            "risk_tag": "immigration_intent_unclear",
            "track": track,
            "question_started_at": now,
            "answered_at": now,
            "late": False,
            "attempt_number": 1,
            "max_attempts": 3,
            "input_mode": "audio",
            "audio_path": "",
            "transcript": "Demo transcript mentioning Nigeria, jobs, and return plan",
            "scores": {
                "correctness": 0.7,
                "content": 0.7,
                "clarity": 0.6,
                "confidence": 0.6,
                "composure": 0.6,
                "risk_tags": ["immigration_intent_unclear"],
                "risk_score": 3,
            },
        },
    ]

    # Simple aggregate: average ~0.64, total risk 8
    overall_scores = {
        "avg_correctness": 0.67,
        "avg_content": 0.60,
        "avg_clarity": 0.60,
        "avg_confidence": 0.60,
        "avg_composure": 0.60,
        "total_risk_score": 8.0,
        "overall_avg_5c": 0.61,
        "ready": False,
    }

    return {
        "session_id": session_id,
        "student_id": "DEMO_STUDENT",
        "track": track,
        "country": country,
        "university_code": "ALL",
        "started_at": now,
        "completed_at": now,
        "questions": questions,
        "overall_scores": overall_scores,
        "risk_summary": {},
    }

def seed():
    SESSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    sessions = [
        make_demo_session("UKVI_DEMO_001", "ukvi"),
        make_demo_session("PRECAS_DEMO_001", "pre_cas"),
        make_demo_session("CRED_DEMO_001", "credibility"),
    ]
    with open(SESSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)
    print(f"Seeded {len(sessions)} demo sessions to {SESSIONS_PATH}")

if __name__ == "__main__":
    seed()
