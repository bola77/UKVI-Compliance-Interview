from pathlib import Path
import pandas as pd

def load_questions(track: str, questions_dir: Path) -> pd.DataFrame:
    """
    Load questions CSV for the given track and filter by track.
    """
    if track == "ukvi":
        path = questions_dir / "ukvi_questions.csv"
    elif track == "pre_cas":
        path = questions_dir / "pre_cas_questions.csv"
    elif track == "credibility":
        path = questions_dir / "credibility_questions.csv"
    else:
        raise ValueError(f"Unknown track: {track}")

    df = pd.read_csv(path)
    if "track" in df.columns:
        df = df[df["track"] == track]
    return df
