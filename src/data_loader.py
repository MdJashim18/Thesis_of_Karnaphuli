
import pandas as pd
from pathlib import Path


def load_data(path):
    """
    Load the Month 2 SHM dataset.

    Parameters:
        path: CSV file path

    Returns:
        pandas DataFrame
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    df = pd.read_csv(path)

    # Remove accidental whitespace from column names
    df.columns = df.columns.str.strip()

    # Parse available timestamp columns
    for col in ["received_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce",
                utc=True
            )

    return df
