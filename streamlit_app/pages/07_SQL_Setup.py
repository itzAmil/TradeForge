# streamlit_app/pages/07_SQL_Setup.py

import sys
import os
import streamlit as st

# --- Ensure project root is in sys.path ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- Imports ---
from scripts.setup_sql_tables import create_tables, DB_PATH

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="🗄️ SQL Setup", layout="centered")
st.title("🗄️ SQL Setup")
st.write("Create your SQL tables and initialize the database. ✅")

# -----------------------------
# Show Database Path
# -----------------------------
st.info(f"Database path: `{DB_PATH}`")

# -----------------------------
# Create Tables Button
# -----------------------------
if st.button("⚡ Create SQL Tables"):
    try:
        create_tables()
        st.success("✅ SQL tables created successfully!")
    except Exception as e:
        st.error(f"❌ Failed to create SQL tables: {e}")
