import pandas as pd

def compute_track_summary(sessions):
    if not sessions:
        return pd.DataFrame(columns=["track", "count"])
    df = pd.DataFrame(sessions)
    return (
        df.groupby("track")
        .size()
        .reset_index(name="count")
        .sort_values("track")
    )