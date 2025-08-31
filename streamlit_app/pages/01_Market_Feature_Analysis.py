# streamlit_app/pages/01_Market_Feature_Analysis.py

import sys
import os
import streamlit as st
import pandas as pd
from ml.feature_engineering import compute_technical_indicators

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Set a professional page title
st.set_page_config(page_title="Market Feature Analysis", layout="wide")

st.title("📊 Market Feature Analysis")

# Path to project-level 'data' folder
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

if not os.path.exists(DATA_DIR):
    st.error(f"Data directory not found: {DATA_DIR}")
    st.stop()

# List CSV files in the data folder
csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

if not csv_files:
    st.warning("No CSV files found in the data folder.")
    st.stop()

# File selection dropdown
selected_file = st.selectbox("📁 Select OHLCV CSV file", csv_files)
file_path = os.path.join(DATA_DIR, selected_file)

# Load CSV
try:
    df = pd.read_csv(file_path)
    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.head())
except Exception as e:
    st.error(f"Failed to load file: {e}")
    st.stop()

# Compute technical indicators
if st.button("⚙️ Compute Technical Indicators"):
    try:
        df_ind = compute_technical_indicators(df)
        st.success("✅ Technical indicators computed successfully!")
        st.subheader("📈 Enhanced Data Preview")
        st.dataframe(df_ind.head())

        # Download button for enhanced CSV
        st.download_button(
            label="💾 Download Enhanced CSV",
            data=df_ind.to_csv(index=False),
            file_name=f"enhanced_{selected_file}",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error computing indicators: {e}")
