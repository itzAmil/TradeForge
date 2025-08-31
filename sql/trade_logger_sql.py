# sql/trade_logger_sql.py
"""
TradeForge: SQL Trade Logger
-----------------------------
Logs executed trades (from ML predictions, RSI signals, etc.) into the SQLite database.

Author: Amil
"""

import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql.models import Trade

# -------------------------------------
# SQLite Database Configuration
# -------------------------------------
DATABASE_URL = "sqlite:///sql/tradeforge.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# -------------------------------------
# Trade Logging Function
# -------------------------------------
def log_trade_to_sql(symbol: str, side: str, quantity: float, price: float, source: str) -> None:
    """
    Logs a trade record into the 'trades' SQL table.

    Parameters:
        symbol (str): Trading pair (e.g., 'BTCUSDT')
        side (str): Trade direction ('BUY' or 'SELL')
        quantity (float): Amount traded
        price (float): Trade execution price
        source (str): Signal source (e.g., 'ml_prediction', 'rsi_signal')
    """
    session = Session()
    try:
        trade = Trade(
            id=str(uuid.uuid4()),             # Generate unique ID
            timestamp=datetime.utcnow(),      # UTC timestamp
            symbol=symbol,
            side=side.upper(),
            quantity=quantity,
            price=price,
            source=source
        )
        session.add(trade)
        session.commit()
        print(f"[✔] Trade logged: {trade}")
    except Exception as e:
        session.rollback()
        print(f"[!] Failed to log trade: {e}")
    finally:
        session.close()

# -------------------------------------
# Example Usage (For Testing Only)
# -------------------------------------
if __name__ == "__main__":
    # Sample trade log for testing (remove/comment in production)
    log_trade_to_sql("BTCUSDT", "BUY", 0.001, 29100.50, "ml_prediction")
