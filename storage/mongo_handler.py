#storage/mongo_handler.py
from pymongo import MongoClient, errors
from utils.tradeforge_logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# ----------------------------------------
# TradeForge MongoDB Handler (NoSQL Layer)
# ----------------------------------------

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["tradeforge_data"]


def insert_ohlcv(symbol: str, interval: str, ohlcv_data: list) -> int:
    """
    Insert OHLCV data into MongoDB for a specific symbol and interval.

    Args:
        symbol (str): Trading pair (e.g., 'BTCUSDT')
        interval (str): Time interval (e.g., '1m')
        ohlcv_data (list of dict): List of OHLCV candles

    Returns:
        int: Number of documents successfully inserted
    """
    if not ohlcv_data:
        logger.warning(f"No OHLCV data received for {symbol} ({interval}). Skipping insert.")
        return 0

    collection_name = f"{symbol}_{interval}"
    collection = db[collection_name]

    try:
        existing_timestamps = {
            doc["timestamp"] for doc in collection.find({}, {"timestamp": 1})
        }

        new_candles = [doc for doc in ohlcv_data if doc["timestamp"] not in existing_timestamps]

        if not new_candles:
            logger.info(f"No new OHLCV data to insert for {symbol} ({interval}).")
            return 0

        result = collection.insert_many(new_candles)
        logger.info(f"Inserted {len(result.inserted_ids)} OHLCV records for {symbol} ({interval}).")
        return len(result.inserted_ids)

    except errors.PyMongoError as e:
        logger.error(f"[MongoDB Insert Error] {symbol} ({interval}): {e}")
        return 0


def get_all_symbols_and_intervals():
    """
    Get all (symbol, interval) pairs stored in the MongoDB collections.

    Returns:
        list of (symbol, interval) tuples.
    """
    try:
        collections = db.list_collection_names()
        symbol_interval_pairs = []

        for name in collections:
            if "_" in name:
                parts = name.split("_")
                symbol = "_".join(parts[:-1])
                interval = parts[-1]
                symbol_interval_pairs.append((symbol, interval))

        return symbol_interval_pairs

    except Exception as e:
        logger.error(f"[MongoDB Error] Failed to fetch collection names: {e}")
        return []
