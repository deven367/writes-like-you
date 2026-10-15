import pandas as pd


def merge_entries(df):
    """Keep one chronological entry per UTC creation date, retaining every page ID."""
    df = df.copy()
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df["date"] = df["ts"].dt.strftime("%Y-%m-%d")
    df["text"] = df["text"].fillna("")
    df = df.sort_values(["ts", "id"], kind="stable")
    return df.groupby("date", as_index=False, sort=True).agg(
        id=("id", ",".join),
        ts=("ts", "min"),
        text=("text", lambda texts: "\n\n".join(text for text in texts if text)),
    )[["id", "ts", "date", "text"]]
