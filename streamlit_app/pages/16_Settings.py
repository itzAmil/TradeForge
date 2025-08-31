# streamlit_app/16_Settings.py
import streamlit as st
import json
import os
from datetime import datetime

# -----------------------
# Config File Paths
# -----------------------

CONFIG_DIR = "config"
AUTO_TRADING_PATH = os.path.join(CONFIG_DIR, "auto_trading_status.json")
STRATEGY_PARAMS_PATH = os.path.join(CONFIG_DIR, "strategy_params.json")

# -----------------------
# JSON Helpers
# -----------------------

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_json_config(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json_config(path, data):
    ensure_config_dir()
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------
# UI Config
# -----------------------

st.set_page_config(page_title="TradeForge Config", layout="centered")
st.title("🔧 TradeForge Strategy Configuration")

# -----------------------
# Section 1: Auto-Trading Toggle
# -----------------------

st.subheader("1. Auto-Trading Control")

auto_config = load_json_config(AUTO_TRADING_PATH, {"enabled": False})
auto_enabled = st.toggle("✅ Enable Auto-Trading", value=auto_config.get("enabled", False))

if st.button("💾 Save Auto-Trading Status"):
    save_json_config(AUTO_TRADING_PATH, {"enabled": auto_enabled})
    st.success(f"Auto-trading status updated to {'ENABLED' if auto_enabled else 'DISABLED'} at {datetime.now().strftime('%H:%M:%S')}")

# -----------------------
# Section 2: Strategy Parameters
# -----------------------

st.subheader("2. Strategy Parameters")

default_strategy = {
    "rsi_period": 14,
    "rsi_buy_threshold": 30,
    "rsi_sell_threshold": 70,
    "ml_model": "RandomForest"
}

strategy_config = load_json_config(STRATEGY_PARAMS_PATH, default_strategy)

# RSI Settings
rsi_period = st.number_input("RSI Period", min_value=2, max_value=100, value=strategy_config.get("rsi_period", 14))
rsi_buy = st.slider("RSI Buy Threshold", min_value=0, max_value=100, value=strategy_config.get("rsi_buy_threshold", 30))
rsi_sell = st.slider("RSI Sell Threshold", min_value=0, max_value=100, value=strategy_config.get("rsi_sell_threshold", 70))

# ML Model
ml_model = st.selectbox("ML Model", ["RandomForest", "XGBoost"], 
                        index=["RandomForest", "XGBoost"].index(strategy_config.get("ml_model", "RandomForest")))

if st.button("💾 Save Strategy Parameters"):
    updated_config = {
        "rsi_period": rsi_period,
        "rsi_buy_threshold": rsi_buy,
        "rsi_sell_threshold": rsi_sell,
        "ml_model": ml_model
    }
    save_json_config(STRATEGY_PARAMS_PATH, updated_config)
    st.success(f"Strategy parameters updated at {datetime.now().strftime('%H:%M:%S')}")

# -----------------------
# Footer
# -----------------------

st.markdown("---")
st.caption("TradeForge Config Panel · Modify strategy & trading behavior live.")
