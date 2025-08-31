# streamlit_app/pages/08_Pipeline_Runner.py

"""
TradeForge Data Pipeline UI
---------------------------
Streamlit interface to run the pipeline and view results.

Author: Amil
"""

import os
import sys
import streamlit as st
import pandas as pd

# === Fix Import Path ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipelines.run_pipeline import run_data_pipeline

# === Try MongoDB Connection ===
use_mongo = True
collection = None
try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.server_info()  # test connection
    db = client["tradeforge_db"]
    collection = db["ohlcv_data"]
except Exception:
    use_mongo = False

# === Streamlit Page Config ===
st.set_page_config(page_title="🚀 Pipeline Runner", layout="wide")
st.title("🚀 Pipeline Runner")
st.markdown("Run the pipeline to fetch OHLCV data, compute indicators, and store them. ✅")

# === Run Pipeline Button ===
if st.button("⚡ Run Pipeline"):
    with st.spinner("Running data pipeline... please wait ⏳"):
        try:
            df_result = run_data_pipeline()

            if df_result.empty:
                st.warning("⚠️ Pipeline finished but returned no data.")
            else:
                # MongoDB available
                if use_mongo and collection is not None:
                    st.success("✅ Pipeline executed successfully! Data saved to MongoDB.")

                    latest_data = list(collection.find().sort("timestamp", -1).limit(50))
                    if latest_data:
                        df = pd.DataFrame(latest_data)
                        st.subheader("🗂️ Latest Inserted Data (50 rows from MongoDB)")
                        st.dataframe(df)
                    else:
                        st.warning("⚠️ No data found in MongoDB after pipeline run.")

                # MongoDB not available → save to CSV
                else:
                    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "pipeline_output.csv")
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    df_result.to_csv(output_path, index=False)

                    st.success(f"✅ Pipeline executed successfully! Data saved locally: `data/pipeline_output.csv`")
                    st.subheader("🗂️ Pipeline Output Preview")
                    st.dataframe(df_result.head(50))

        except Exception as e:
            st.error(f"❌ Error running pipeline: {str(e)}")

# === Sidebar Info ===
st.sidebar.header("ℹ️ Info")
st.sidebar.write(
    "This tool runs the TradeForge data pipeline.\n\n"
    "- If MongoDB is available → results stored in `tradeforge_db.ohlcv_data`.\n"
    "- If MongoDB is not available → results saved locally as `data/pipeline_output.csv`.\n"
    "- In both cases → a preview of the processed data is shown."
)
