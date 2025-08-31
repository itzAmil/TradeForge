# streaming/websocket_streamer.py
"""
TradeForge: WebSocket Streaming & Auto-Trading Engine
------------------------------------------------------
Streams live OHLCV candles from Binance, computes RSI,
makes ML predictions, logs to SQL, and executes trades 
based on prediction signal with cooldown + toggle config.

Author: Amil
"""

import json
import time
import threading
import websocket
import pandas as pd
import joblib
import os
import sys  # 🔹 added

# ────────────────────────────────────────────────────────────────
# Path Setup: Ensure project root and sql/ are on sys.path
# ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

SQL_DIR = os.path.join(BASE_DIR, "sql")
if SQL_DIR not in sys.path:
    sys.path.append(SQL_DIR)

# ────────────────────────────────────────────────────────────────
# Internal Imports (now safe)
# ────────────────────────────────────────────────────────────────
from utils.tradeforge_logger import setup_logger
from signal_engine.indicators_core import calculate_rsi
from sql_handler import insert_ohlcv_sql, insert_predictions_sql  # 🔹 updated import
from services.trade_executor import place_test_order

# ────────────────────────────────────────────────────────────────
# Logger & Model Initialization
# ────────────────────────────────────────────────────────────────
logger = setup_logger(__name__)

MODEL_DIR = os.path.join(BASE_DIR, "ml", "models")

PRIMARY_MODEL_PATH = os.path.join(MODEL_DIR, "random_forest.pkl")
FALLBACK_MODEL_PATH = os.path.join(MODEL_DIR, "xgboost.pkl")

model = None
model_name = None

try:
    model = joblib.load(PRIMARY_MODEL_PATH)
    model_name = "Random Forest"
    logger.info("✔ Loaded primary model: Random Forest")
except FileNotFoundError:
    logger.warning("Primary model not found. Attempting fallback...")
    try:
        model = joblib.load(FALLBACK_MODEL_PATH)
        model_name = "XGBoost"
        logger.info("✔ Loaded fallback model: XGBoost")
    except FileNotFoundError:
        logger.error("No model available. Prediction will be skipped.")

# ────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────
SYMBOL = "btcusdt"
INTERVAL = "1m"
STREAM_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@kline_{INTERVAL}"

TRADE_QUANTITY = 0.001
TRADE_INTERVAL_SECONDS = 300
last_trade_time = 0

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

AUTO_TRADING_CONFIG_PATH = os.path.join(BASE_DIR, "config", "auto_trading_status.json")

# ────────────────────────────────────────────────────────────────
# Thread-safe storage for live logs / predictions
# ────────────────────────────────────────────────────────────────
_latest_entries = []
_entries_lock = threading.Lock()
MAX_ENTRIES = 100  # store last 100 entries

def get_latest_entries(limit=10):
    """Return the latest `limit` entries in a thread-safe way."""
    with _entries_lock:
        return list(_latest_entries[-limit:])

def append_entry(entry: dict):
    """Append a new log/prediction entry safely."""
    with _entries_lock:
        _latest_entries.append(entry)
        if len(_latest_entries) > MAX_ENTRIES:
            _latest_entries.pop(0)

# ────────────────────────────────────────────────────────────────
# Utility Functions
# ────────────────────────────────────────────────────────────────
def is_auto_trading_enabled() -> bool:
    try:
        with open(AUTO_TRADING_CONFIG_PATH, "r") as f:
            config = json.load(f)
            return config.get("enabled", False)
    except FileNotFoundError:
        logger.warning("Auto-trading config not found. Defaulting to disabled.")
        return False

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    features = ['open', 'high', 'low', 'close', 'volume', 'rsi']
    return df[features].tail(1)

def should_place_trade(prediction: int, last_trade_time: float) -> bool:
    return (time.time() - last_trade_time) >= TRADE_INTERVAL_SECONDS

# ────────────────────────────────────────────────────────────────
# WebSocket Event Handlers
# ────────────────────────────────────────────────────────────────
def on_message(ws, message):
    global last_trade_time

    try:
        data = json.loads(message)
        kline = data['k']
        if not kline['x']:
            return

        candle = {
            'timestamp': pd.to_datetime(kline['t'], unit='ms'),
            'open': float(kline['o']),
            'high': float(kline['h']),
            'low': float(kline['l']),
            'close': float(kline['c']),
            'volume': float(kline['v'])
        }

        df = pd.DataFrame([candle])
        df['rsi'] = calculate_rsi(df, period=RSI_PERIOD)

        # Handle insufficient candles gracefully
        if df['rsi'].isnull().any():
            logger.info(f"⏳ Waiting for RSI (need at least {RSI_PERIOD} candles)...")
            return

        try:
            insert_ohlcv_sql(SYMBOL.upper(), INTERVAL, df)
        except Exception as e:
            logger.warning(f"SQL insert failed (OHLCV): {e}")

        if model:
            X = preprocess_data(df)
            prediction = model.predict(X)[0]
            logger.info(
                f"[{model_name}] Prediction: {prediction} | "
                f"Close: {df['close'].iloc[0]:.2f} | RSI: {df['rsi'].iloc[0]:.2f}"
            )
        else:
            prediction = None
            logger.warning("Model not loaded. Skipping prediction.")

        entry = {
            "timestamp": candle['timestamp'],
            "symbol": SYMBOL.upper(),
            "close": candle['close'],
            "rsi": df['rsi'].iloc[0],
            "prediction": prediction
        }
        append_entry(entry)

        try:
            df['prediction'] = prediction
            df['confidence'] = None
            insert_predictions_sql(SYMBOL.upper(), INTERVAL, df)
        except Exception as e:
            logger.warning(f"SQL insert failed (Prediction): {e}")

        if is_auto_trading_enabled() and prediction in [1, -1]:
            if should_place_trade(prediction, last_trade_time):
                action = "BUY" if prediction == 1 else "SELL"
                logger.info(f"Placing {action} order...")
                place_test_order(SYMBOL.upper(), action, TRADE_QUANTITY)
                last_trade_time = time.time()
        else:
            logger.info("Auto-trading disabled or no actionable signal.")

    except Exception as e:
        logger.exception("Exception in WebSocket message handler")

def on_error(ws, error):
    logger.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    logger.info("WebSocket connection closed.")

def on_open(ws):
    logger.info(f"WebSocket connected: {STREAM_URL}")

# ────────────────────────────────────────────────────────────────
# Start / Stop WebSocket Stream (singleton)
# ────────────────────────────────────────────────────────────────
_ws_thread = None
_ws_running = False
_ws_app = None

def start_stream():
    global _ws_thread, _ws_running, _ws_app
    if _ws_running:
        logger.info("⚠️ WebSocket stream already running. Skipping duplicate start.")
        return

    _ws_running = True  # set immediately to prevent race conditions

    def run():
        global _ws_app, _ws_running
        _ws_app = websocket.WebSocketApp(
            STREAM_URL,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        try:
            _ws_app.run_forever()
        finally:
            _ws_running = False
            _ws_app = None

    _ws_thread = threading.Thread(target=run, daemon=True)
    _ws_thread.start()
    logger.info("🚀 WebSocket stream started.")

def stop_stream():
    global _ws_app, _ws_running
    if not _ws_running:
        logger.info("ℹ️ No active WebSocket stream to stop.")
        return
    if _ws_app:
        logger.info("🛑 Closing WebSocket stream...")
        _ws_app.close()
    _ws_running = False

# ────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"Starting TradeForge WebSocket for {SYMBOL.upper()} [{INTERVAL}]...")
    start_stream()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_stream()
        logger.info("Stopped by user.")
