#scripts/setup_sql_tables.py
import sys
import os

# --- Ensure project root is in sys.path ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- Now import from sql package ---
from sql.models import Base
from sqlalchemy import create_engine

# === SQLite DB Path ===
DB_DIR = os.path.join(ROOT_DIR, "sql")
DB_FILENAME = "escalade.db"
DB_PATH = os.path.join(DB_DIR, DB_FILENAME)

os.makedirs(DB_DIR, exist_ok=True)

def create_tables():
    """Initializes all tables defined in models.py."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(engine)

    if os.path.exists(DB_PATH):
        print(f"✅ All SQL tables created successfully in: {DB_PATH}")
    else:
        print("❌ Table creation failed. DB not found.")


if __name__ == "__main__":
    create_tables()
