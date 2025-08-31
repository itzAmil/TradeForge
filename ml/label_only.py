# ml/label_only.py

import os
import pandas as pd
from ml.label_generator import generate_labels

INPUT_CSV = "data/BTCUSDT_15m.csv"
OUTPUT_CSV = "data/BTCUSDT_15m_labeled.csv"

def save_labeled_dataset(input_csv: str, output_csv: str) -> None:
    """
    Load OHLCV CSV with indicators → apply signal labels → save labeled CSV.

    Note: Assumes indicators are already computed.
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    df = pd.read_csv(input_csv).dropna()

    df_labeled = generate_labels(df, threshold=0.002, future_window=5)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_labeled.to_csv(output_csv, index=False)

    print(f"[✔] Labeled dataset saved to: {output_csv}")
    print(f"Columns: {df_labeled.columns.tolist()}")

if __name__ == "__main__":
    save_labeled_dataset(INPUT_CSV, OUTPUT_CSV)
