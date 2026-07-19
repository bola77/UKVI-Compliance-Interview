import json
from pathlib import Path
from typing import List, Dict

def load_sessions(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
