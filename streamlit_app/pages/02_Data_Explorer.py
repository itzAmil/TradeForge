# streamlit_app/pages/02_Data_Explorer.py

import streamlit as st
import pandas as pd
import os

# Resolve absolute path to the root-level data folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# Set a professional page title
st.set_page_config(page_title="Data Explorer", layout="wide")
st.title("🗂️ Data Explorer")

# List CSV files in the data directory
if not os.path.exists(DATA_DIR):
    st.error(f"Data directory not found: {DATA_DIR}")
else:
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

    if not csv_files:
        st.warning("No CSV files found in the data folder.")
    else:
        selected_file = st.selectbox("📁 Select a CSV file to view", csv_files)
        file_path = os.path.join(DATA_DIR, selected_file)

        try:
            df = pd.read_csv(file_path)

            # Show folder/filename in UI
            st.markdown(f"**📄 File Path:** `{os.path.relpath(file_path, PROJECT_ROOT)}`")

            st.subheader(f"🔍 Preview of `{selected_file}`")
            st.dataframe(df)

            st.download_button(
                label="💾 Download CSV",
                data=df.to_csv(index=False),
                file_name=selected_file,
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Failed to load file: {e}")
