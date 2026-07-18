import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
SESSIONS_PATH = BASE / "data" / "session_exports" / "sessions.json"

def append_session(session: dict) -> None:
    """
    Append a completed session to sessions.json.
    """
    SESSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SESSIONS_PATH.exists():
        with open(SESSIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(session)
    with open(SESSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)