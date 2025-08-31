# sql/sql_handler.py
"""
TradeForge SQL Handler
-----------------------
This module handles INSERT operations into the SQL database (Escalade).
Used for writing:
- OHLCV market data
- Technical indicators (SMA, EMA, RSI)
- ML predictions (Buy/Sell/Hold)

Also exposes a session getter for external scripts.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sql.models import OHLCV, Indicator, MLPrediction

import pandas as pd

# === SQLite Engine and Session ===
DB_PATH = "sqlite:///sql/escalade.db"
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)

# ----------------------------------------------------------
# Insert OHLCV Data (if not exists)
# ----------------------------------------------------------
def insert_ohlcv_sql(symbol: str, interval: str, df: pd.DataFrame) -> int:
    """
    Insert OHLCV candles into the SQL database if not already present.

    Returns:
        int: Number of rows inserted
    """
    session = Session()
    inserted = 0

    try:
        for _, row in df.iterrows():
            timestamp = pd.to_datetime(row["timestamp"], unit="ms")
            exists = session.query(OHLCV).filter_by(
                symbol=symbol, interval=interval, timestamp=timestamp
            ).first()
            if exists:
                continue

            candle = OHLCV(
                symbol=symbol,
                interval=interval,
                timestamp=timestamp,
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"]
            )
            session.add(candle)
            inserted += 1

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"[SQL INSERT ERROR - OHLCV] {e}")

    finally:
        session.close()

    return inserted

# ----------------------------------------------------------
# Insert Technical Indicators
# ----------------------------------------------------------
def insert_indicators_sql(symbol: str, interval: str, df: pd.DataFrame) -> int:
    """
    Insert SMA, EMA, RSI values linked to OHLCV rows.

    Returns:
        int: Number of indicator rows inserted
    """
    session = Session()
    inserted = 0

    try:
        for _, row in df.iterrows():
            timestamp = pd.to_datetime(row["timestamp"], unit="ms")
            ohlcv_row = session.query(OHLCV).filter_by(
                symbol=symbol, interval=interval, timestamp=timestamp
            ).first()

            if not ohlcv_row or ohlcv_row.indicator:
                continue

            ind = Indicator(
                ohlcv_id=ohlcv_row.id,
                sma=row.get("sma"),
                ema=row.get("ema"),
                rsi=row.get("rsi")
            )
            session.add(ind)
            inserted += 1

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"[SQL INSERT ERROR - INDICATORS] {e}")

    finally:
        session.close()

    return inserted

# ----------------------------------------------------------
# Insert ML Predictions
# ----------------------------------------------------------
def insert_predictions_sql(symbol: str, interval: str, df: pd.DataFrame) -> int:
    """
    Insert ML-based prediction labels linked to OHLCV rows.

    Returns:
        int: Number of prediction rows inserted
    """
    session = Session()
    inserted = 0

    try:
        for _, row in df.iterrows():
            timestamp = pd.to_datetime(row["timestamp"], unit="ms")
            ohlcv_row = session.query(OHLCV).filter_by(
                symbol=symbol, interval=interval, timestamp=timestamp
            ).first()

            if not ohlcv_row or ohlcv_row.prediction:
                continue

            pred = MLPrediction(
                ohlcv_id=ohlcv_row.id,
                prediction=row.get("prediction")
            )
            session.add(pred)
            inserted += 1

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"[SQL INSERT ERROR - PREDICTIONS] {e}")

    finally:
        session.close()

    return inserted

# ----------------------------------------------------------
# External Access: Get SQL Session
# ----------------------------------------------------------
def get_sql_session():
    """
    Returns a SQLAlchemy session (for read-only scripts).
    """
    return Session()
