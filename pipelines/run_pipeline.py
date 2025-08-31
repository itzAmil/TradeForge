# pipelines/run_pipeline.py
"""
TradeForge Data Pipeline Script
-------------------------------
Fetches OHLCV data from Binance, calculates indicators (SMA, EMA, RSI, MACD),
and stores the enriched dataset into MongoDB.

Author: Amil
"""

import logging
import pandas as pd
from pymongo import MongoClient

from api.exchange_api import fetch_ohlcv
from signal_engine.indicators_core import (
    calculate_sma, calculate_ema,
    calculate_rsi, calculate_macd
)

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# === MongoDB Setup ===
client = MongoClient("mongodb://localhost:27017/")
db = client["tradeforge_db"]
collection = db["ohlcv_data"]

# === Symbols & Intervals ===
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
INTERVALS = ["1m", "5m", "15m"]


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all technical indicators on a DataFrame."""
    df["sma_14"] = calculate_sma(df, 14)
    df["ema_14"] = calculate_ema(df, 14)
    df["rsi_14"] = calculate_rsi(df, 14)

    macd_df = calculate_macd(df)
    df = pd.concat([df, macd_df], axis=1)

    return df


def insert_data(symbol: str, interval: str, df: pd.DataFrame) -> int:
    """Insert processed DataFrame into MongoDB after validation. Returns # inserted."""
    if df.empty:
        logging.warning(f"❌ No data for {symbol} [{interval}]. Skipping insert.")
        return 0

    # Ensure timestamp is datetime
    if pd.api.types.is_numeric_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Add metadata
    df["symbol"] = symbol
    df["interval"] = interval

    data_dict = df.to_dict("records")
    if not data_dict:
        logging.warning(f"⚠ Nothing to insert for {symbol} [{interval}]")
        return 0

    result = collection.insert_many(data_dict)
    inserted_count = len(result.inserted_ids)
    logging.info(f"✅ Inserted {inserted_count} records for {symbol} [{interval}]")
    return inserted_count


def run_data_pipeline() -> pd.DataFrame:
    """
    Run the data pipeline: fetch → calculate indicators → store in MongoDB.
    Returns a combined DataFrame of all processed records.
    """
    success_count = 0
    fail_count = 0
    all_dataframes = []

    for symbol in SYMBOLS:
        for interval in INTERVALS:
            logging.info(f"\n{'=' * 60}\nStarting pipeline for {symbol} [{interval}]\n{'=' * 60}")

            df = fetch_ohlcv(symbol, interval)

            # ✅ Always convert to DataFrame if list
            if isinstance(df, list):
                df = pd.DataFrame(df)

            if not isinstance(df, pd.DataFrame):
                logging.error(f"Unexpected data format from fetch_ohlcv for {symbol} [{interval}] → {type(df)}")
                fail_count += 1
                continue

            if df.empty:
                logging.warning(f"No data returned for {symbol} [{interval}]")
                fail_count += 1
                continue

            df = calculate_indicators(df)
            inserted = insert_data(symbol, interval, df)

            if inserted > 0:
                success_count += 1
                all_dataframes.append(df)
            else:
                fail_count += 1

    logging.info(f"\n✅ Pipeline completed. Success: {success_count} | Failures: {fail_count}")

    # Return combined DataFrame (if nothing, return empty DF)
    if all_dataframes:
        return pd.concat(all_dataframes, ignore_index=True)
    return pd.DataFrame()


# === Entry Point ===
if __name__ == "__main__":
    combined_df = run_data_pipeline()
    if not combined_df.empty:
        print(f"Pipeline finished → {len(combined_df)} rows processed.")
    else:
        print("Pipeline finished → No data processed.")
