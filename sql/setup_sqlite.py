# sql/setup_sqlite.py
"""
TradeForge: SQLite Database Initializer
---------------------------------------
Initializes the hybrid SQL database (escalade.db) and creates all required tables:
- OHLCV market data
- Technical indicators (SMA, EMA, RSI)
- ML predictions (Buy/Sell/Hold)
- Executed trades (auto-trading logs)

Author: Amil
"""

from sqlalchemy import create_engine
from sql.models import Base  # Includes OHLCV, Indicator, MLPrediction, Trade

# Default path to SQLite DB (relative to project root)
DEFAULT_DB_PATH = "sqlite:///sql/tradeforge.db"

def init_sqlite_db(db_path: str = DEFAULT_DB_PATH):
    """
    Initializes the SQLite database using SQLAlchemy and creates all tables.

    Args:
        db_path (str): SQLAlchemy-compatible DB URI (default = 'sqlite:///sql/tradeforge.db')
    """
    try:
        engine = create_engine(db_path)
        Base.metadata.create_all(engine)
        print(f"[✔] SQLite database and tables created successfully at: {db_path}")
    except Exception as e:
        print(f"[✘] Database initialization failed: {e}")

if __name__ == "__main__":
    init_sqlite_db()
