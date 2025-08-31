# sql/models.py
"""
TradeForge SQLAlchemy Models
-----------------------------
Defines hybrid SQL storage schema for:
1. OHLCV data
2. Technical indicators (SMA, EMA, RSI)
3. Machine learning predictions (Buy/Sell/Hold)
4. Auto-Executed Trade Logs
"""

from sqlalchemy import (
    Column, Integer, Float, String, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# -------------------------
# Table: OHLCV Market Data
# -------------------------
class OHLCV(Base):
    __tablename__ = "ohlcv_data"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True, nullable=False)       # e.g., BTCUSDT
    interval = Column(String, nullable=False)                  # e.g., '1m', '5m'
    timestamp = Column(DateTime, index=True, unique=True, nullable=False)

    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    # Relationships
    indicator = relationship("Indicator", back_populates="ohlcv", uselist=False)
    prediction = relationship("MLPrediction", back_populates="ohlcv", uselist=False)

    def __repr__(self):
        return f"<OHLCV(symbol={self.symbol}, interval={self.interval}, timestamp={self.timestamp})>"


# ----------------------------------
# Table: Technical Indicators
# ----------------------------------
class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    ohlcv_id = Column(Integer, ForeignKey("ohlcv_data.id"), nullable=False)

    sma = Column(Float, nullable=True)
    ema = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)

    ohlcv = relationship("OHLCV", back_populates="indicator")

    def __repr__(self):
        return f"<Indicator(sma={self.sma}, ema={self.ema}, rsi={self.rsi})>"


# -----------------------------------
# Table: ML Predictions (Buy/Sell/Hold)
# -----------------------------------
class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True)
    ohlcv_id = Column(Integer, ForeignKey("ohlcv_data.id"), nullable=False)
    prediction = Column(Integer, nullable=False)  # 1 = Buy, -1 = Sell, 0 = Hold

    ohlcv = relationship("OHLCV", back_populates="prediction")

    def __repr__(self):
        return f"<MLPrediction(prediction={self.prediction})>"


# ----------------------------------------
# Table: Auto-Executed Trades
# ----------------------------------------
class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True)  # UUID or custom string ID
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String)
    side = Column(String)         # 'BUY' or 'SELL'
    quantity = Column(Float)
    price = Column(Float)
    source = Column(String)       # Source of signal: 'ml_prediction', 'rsi_signal', etc.

    def __repr__(self):
        return f"<Trade(symbol={self.symbol}, side={self.side}, quantity={self.quantity}, price={self.price}, source={self.source})>"
