#scripts/seed_db_from_csv.py
"""
seed_db_from_csv.py
--------------------
Loads OHLCV data from CSV and inserts rows into SQLite DB for Streamlit dashboard.

Target:
- symbol = "BTCUSDT"
- interval = "15m"
- OHLCV rows into ohlcv_data table
- Dummy SMA/EMA/RSI rows into indicators table
- Dummy predictions into ml_predictions table
"""

import os
import sys
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql.models import OHLCV, Indicator, MLPrediction

DB_PATH = os.path.join(ROOT_DIR, "sql", "escalade.db")
CSV_PATH = os.path.join("data", "BTCUSDT_15m.csv")

# Change to match Streamlit filters
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_INTERVAL = "15m"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)
Session = sessionmaker(bind=engine)

def seed_database_from_csv():
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] CSV file not found: {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)
    print(f"[INFO] Loaded CSV with {len(df)} rows")

    # Ensure timestamp column
    if 'timestamp' not in df.columns:
        print("[ERROR] CSV missing 'timestamp' column.")
        return

    # Open database session
    session = Session()
    try:
        inserted_count = 0
        for _, row in df.iterrows():
            ts = pd.to_datetime(row["timestamp"])

            # Insert OHLCV row
            ohlcv_obj = OHLCV(
                symbol=DEFAULT_SYMBOL,
                interval=DEFAULT_INTERVAL,
                timestamp=ts,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row.get("volume", 0.0))
            )
            session.add(ohlcv_obj)
            session.flush()  # Get the ohlcv_obj.id

            # Indicator placeholder
            ind_obj = Indicator(
                ohlcv_id=ohlcv_obj.id,
                sma=0.0,
                ema=0.0,
                rsi=0.0
            )
            session.add(ind_obj)

            # Dummy prediction
            pred_obj = MLPrediction(
                ohlcv_id=ohlcv_obj.id,
                prediction=0
            )
            session.add(pred_obj)

            inserted_count += 1

        session.commit()
        print(f"[SUCCESS] Inserted {inserted_count} OHLCV records into DB")

    except Exception as e:
        session.rollback()
        print("[ERROR] Database insert failed:", e)

    finally:
        session.close()

if __name__ == "__main__":
    seed_database_from_csv()

