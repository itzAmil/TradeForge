#scripts/check_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql.models import OHLCV

engine = create_engine("sqlite:///sql/escalade.db")
Session = sessionmaker(bind=engine)
session = Session()

rows = session.query(OHLCV).limit(5).all()
for r in rows:
    print(r.symbol, r.interval, r.timestamp)
