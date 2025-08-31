# streamlit_app/pages/05_SQL_Verifier.py

import os
import sys
import streamlit as st

# --- Add project root to sys.path for imports ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- Imports ---
from sql.sql_handler import get_sql_session
from sql.models import OHLCV, Indicator, MLPrediction

# --- Page Configuration ---
st.set_page_config(page_title="SQL Verifier", page_icon="🕵️‍♂️", layout="centered")
st.title("🕵️‍♂️ SQL Verifier")
st.write("Check the row counts of key SQL tables in your database. ✅")

# --- Verify Button ---
if st.button("🔍 Verify Data"):
    session = get_sql_session()
    try:
        ohlcv_count = session.query(OHLCV).count()
        indicator_count = session.query(Indicator).count()
        prediction_count = session.query(MLPrediction).count()

        st.success("🏆 SQL verification completed successfully!")
        st.metric("📊 OHLCV Data", ohlcv_count)
        st.metric("📈 Indicators", indicator_count)
        st.metric("🤖 ML Predictions", prediction_count)

    except Exception as e:
        st.error(f"❌ Error while verifying SQL data: {e}")

    finally:
        session.close()

