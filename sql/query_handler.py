# sql/query_handler.py
"""
TradeForge SQL Query Handler
-----------------------------
Handles SELECT operations from the SQL database (Escalade).
Fetches recent OHLCV + indicator data and ML predictions.
"""

import os
import sys
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Make sure we can import models even if executed dynamically
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from sql.models import OHLCV, Indicator, MLPrediction

# Use absolute DB path to always connect to the **correct** file
ABSOLUTE_DB_PATH = "sqlite:///C:/Users/Amil/TradeForge/sql/escalade.db"

engine = create_engine(
    ABSOLUTE_DB_PATH,
    connect_args={"check_same_thread": False}
)
Session = sessionmaker(bind=engine)

def fetch_recent_ohlcv(symbol: str, interval: str, limit: int = 100):
    session = Session()
    try:
        query = (
            session.query(OHLCV, Indicator)
            .join(Indicator, OHLCV.id == Indicator.ohlcv_id)
            .filter(OHLCV.symbol == symbol, OHLCV.interval == interval)
            .order_by(OHLCV.timestamp.desc())
            .limit(limit)
        )
        records = query.all()
        data = [
            {
                "timestamp": ohlcv.timestamp,
                "open": ohlcv.open,
                "high": ohlcv.high,
                "low": ohlcv.low,
                "close": ohlcv.close,
                "volume": ohlcv.volume,
                "sma": ind.sma,
                "ema": ind.ema,
                "rsi": ind.rsi,
                "signal": 0
            }
            for ohlcv, ind in reversed(records)
        ]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"[SQL FETCH OHLCV ERROR] {e}")
        return pd.DataFrame()
    finally:
        session.close()

def fetch_recent_predictions(symbol: str, interval: str, limit: int = 100):
    session = Session()
    try:
        query = (
            session.query(OHLCV, MLPrediction)
            .join(MLPrediction, OHLCV.id == MLPrediction.ohlcv_id)
            .filter(OHLCV.symbol == symbol, OHLCV.interval == interval)
            .order_by(OHLCV.timestamp.desc())
            .limit(limit)
        )
        records = query.all()
        data = [
            {
                "timestamp": ohlcv.timestamp,
                "prediction": pred.prediction
            }
            for ohlcv, pred in reversed(records)
        ]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"[SQL FETCH PREDICTION ERROR] {e}")
        return pd.DataFrame()
    finally:
        session.close()
