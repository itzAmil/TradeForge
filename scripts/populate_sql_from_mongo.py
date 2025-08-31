#script/populate_sql_from_mongo.py
"""
Script to populate SQLite database from MongoDB.
Extracts OHLCV + indicators data and stores it in the SQL database.
"""

from pymongo import MongoClient
from sqlalchemy import create_engine
import pandas as pd
import os

# === MongoDB Configuration ===
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "tradeforge_db"
MONGO_COLLECTION = "ohlcv_data"

# === SQLite Configuration ===
SQLITE_PATH = os.path.join(os.getcwd(), "escalade.db")
engine = create_engine(f"sqlite:///{SQLITE_PATH}")

# === MongoDB Connection ===
client = MongoClient(MONGO_URI)
mongo_collection = client[MONGO_DB][MONGO_COLLECTION]

def transfer_data(symbol: str, interval: str):
    """
    Pulls data from MongoDB for a given symbol/interval, 
    then inserts it into corresponding SQLite table.
    """
    query = {"symbol": symbol, "interval": interval}
    cursor = mongo_collection.find(query)

    data = list(cursor)
    if not data:
        print(f"⚠️ No MongoDB data found for {symbol} {interval}")
        return

    df = pd.DataFrame(data)

    # Clean data for SQL compatibility
    df.drop(columns=["_id"], inplace=True, errors="ignore")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df.dropna(subset=["timestamp"], inplace=True)

    # Format table name
    table_name = f"{symbol.lower()}_{interval}"

    try:
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)
        print(f"✅ Inserted {len(df)} records into table: {table_name}")
    except Exception as e:
        print(f"❌ Error inserting {symbol} {interval}: {e}")


def run_sql_populator():
    """
    Transfers data for all configured symbol-interval pairs from MongoDB to SQLite.
    """
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    intervals = ["1m", "5m", "15m"]
    total_tables = 0

    for symbol in symbols:
        for interval in intervals:
            transfer_data(symbol, interval)
            total_tables += 1

    print(f"\n🎉 SQL Sync Complete: {total_tables} tables processed.")


# === Entry Point ===
if __name__ == "__main__":
    run_sql_populator()
