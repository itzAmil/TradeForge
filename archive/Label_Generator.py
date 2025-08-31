# ui/label_generator_ui.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.label_generator import generate_labels

import streamlit as st
import pandas as pd

st.title("📈 Trading Label Generator")
st.write("Generate Buy / Sell / Hold labels from price data.")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV with a 'close' column", type=["csv"])

# User inputs
threshold = st.number_input("Return Threshold (e.g., 0.002 = 0.2%)", value=0.002, format="%.5f")
future_window = st.number_input("Future Window (steps ahead)", value=5, min_value=1, step=1)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "close" not in df.columns:
        st.error("CSV must contain a 'close' column.")
    else:
        # Generate labels
        labeled_df = generate_labels(df, threshold=threshold, future_window=future_window)

        st.subheader("Preview of Labeled Data")
        st.dataframe(labeled_df.head(20))

        # Download option
        csv = labeled_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Labeled Data as CSV",
            data=csv,
            file_name="labeled_data.csv",
            mime="text/csv",
        )
