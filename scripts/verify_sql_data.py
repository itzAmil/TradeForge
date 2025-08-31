#scripts/verify_sql_data.py
"""
Script to verify data population in SQL tables.

Connects to the SQLite DB and prints row counts for:
- OHLCV table
- Indicator table
- MLPrediction table
"""

import os
import sys

# Add root path to access 'sql' modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sql.sql_handler import get_sql_session
from sql.models import OHLCV, Indicator, MLPrediction

def verify_table_data():
    """
    Prints row counts of key SQL tables for data verification.
    """
    session = get_sql_session()

    try:
        ohlcv_count = session.query(OHLCV).count()
        indicator_count = session.query(Indicator).count()
        prediction_count = session.query(MLPrediction).count()

        print("📊 SQL Table Verification:")
        print(f" - OHLCV Data       : {ohlcv_count} rows")
        print(f" - Indicators       : {indicator_count} rows")
        print(f" - ML Predictions   : {prediction_count} rows")
        print("✅ SQL verification completed successfully.")

    except Exception as e:
        print(f"❌ Error while verifying SQL data: {e}")

    finally:
        session.close()

if __name__ == "__main__":
    verify_table_data()
