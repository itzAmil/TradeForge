# ui/predict_ui.py

import sys, os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Path fix: ensure project root is on sys.path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.predict import predict_from_df

st.title("Modelpredictor")
st.write("Upload OHLCV data â†’ compute indicators â†’ apply trained ML model â†’ get Buy/Sell/Hold predictions")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload OHLCV CSV (must have 'close' column)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file).dropna()

    if "close" not in df.columns:
        st.error("CSV must contain a 'close' column.")
    else:
        try:
            # --- Run predictions ---
            df_pred = predict_from_df(df)

            st.subheader("ðŸ” Preview of Predictions")
            st.dataframe(df_pred.head(20))

            # --- Download ---
            csv = df_pred.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="ðŸ’¾ Download Predictions CSV",
                data=csv,
                file_name="predictions.csv",
                mime="text/csv",
            )

            # --- Visualization ---
            st.subheader("ðŸ“ˆ Price Chart with Predictions")

            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df_pred["close"], mode="lines", name="Close Price"))

            # Add prediction markers
            buys = df_pred[df_pred["prediction"] == 1]
            sells = df_pred[df_pred["prediction"] == -1]

            fig.add_trace(go.Scatter(
                x=buys.index, y=buys["close"],
                mode="markers", marker=dict(color="green", size=8, symbol="triangle-up"),
                name="Buy"
            ))
            fig.add_trace(go.Scatter(
                x=sells.index, y=sells["close"],
                mode="markers", marker=dict(color="red", size=8, symbol="triangle-down"),
                name="Sell"
            ))

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Prediction failed: {e}")
