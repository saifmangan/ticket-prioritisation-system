import pandas as pd
from pathlib import Path

from features import build_features

RAW_DATA_PATH = Path("data/raw/tickets.csv")
PROCESSED_DATA_PATH = Path("data/processed/clean_tickets.csv")


def load_data(path: Path) -> pd.DataFrame:
    """Load raw CSV data."""
    return pd.read_csv(path)


def clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = str(text).lower()
    text = text.replace("!", "")
    return text.strip()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset."""
    df = df.copy()
    df["customer_message"] = df["customer_message"].apply(clean_text)
    return df


def save_data(df: pd.DataFrame, path: Path) -> None:
    """Save cleaned data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def run_pipeline():
    df_raw = load_data(RAW_DATA_PATH)
    df_clean = clean_data(df_raw)
    df_feat = build_features(df_clean)
    save_data(df_feat, PROCESSED_DATA_PATH)


if __name__ == "__main__":
    run_pipeline()
    print("Pipeline executed successfully")
