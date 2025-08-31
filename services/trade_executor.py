# services/trade_executor.py
"""
TradeForge Auto-Trading Executor (Simulated)
--------------------------------------------
Places simulated trades (e.g., on Binance Testnet) with a cooldown mechanism.
Trades are logged to a CSV file with timestamps.

Author: Amil
"""

import os
import time
import csv
from datetime import datetime, timezone
from utils.tradeforge_logger import setup_logger

# -----------------------------
# Configuration
# -----------------------------
TRADE_COOLDOWN_SECONDS = 300  # 5 minutes
TRADE_LOG_PATH = "data/trade_log.csv"
LAST_TRADE_TIME = 0  # Global cooldown timer

# Ensure data directory exists
os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)

# -----------------------------
# Logger
# -----------------------------
logger = setup_logger(__name__)

# -----------------------------
# Trade Executor
# -----------------------------
def place_test_order(symbol: str, side: str, quantity: float = 0.001) -> None:
    """
    Places a simulated trade for a given symbol and logs the result.

    Parameters:
    - symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
    - side (str): 'BUY' or 'SELL'
    - quantity (float): Trade quantity (default: 0.001)
    """
    global LAST_TRADE_TIME
    current_time = time.time()

    # Enforce trade cooldown
    if current_time - LAST_TRADE_TIME < TRADE_COOLDOWN_SECONDS:
        logger.warning("Trade blocked: cooldown in effect. Try later.")
        return

    # Update cooldown
    LAST_TRADE_TIME = current_time
    # Use timezone-aware UTC timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Simulate API call (for Binance Testnet)
    logger.info(f"Placing TESTNET {side} order | Symbol: {symbol} | Qty: {quantity}")

    # Write trade log to CSV
    file_exists = os.path.isfile(TRADE_LOG_PATH)
    with open(TRADE_LOG_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "symbol", "side", "quantity"])
        writer.writerow([timestamp, symbol, side, quantity])

    logger.info(f"Trade logged at {timestamp}")
