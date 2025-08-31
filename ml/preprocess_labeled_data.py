# ml/preprocess_and_label.py

import sys
import os
import pandas as pd

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.feature_engineering import compute_technical_indicators
from ml.label_generator import generate_labels

# === Default Paths ===
INPUT_PATH = "data/BTCUSDT_15m.csv"
OUTPUT_PATH = "data/BTCUSDT_15m_labeled.csv"

def process_and_label_data(input_path: str, output_path: str) -> None:
    """
    Load OHLCV CSV → Compute indicators + labels → Save new labeled CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)

    df = compute_technical_indicators(df)
    df = generate_labels(df)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"[✔] Labeled data saved to: {output_path}")

if __name__ == "__main__":
    process_and_label_data(INPUT_PATH, OUTPUT_PATH)
