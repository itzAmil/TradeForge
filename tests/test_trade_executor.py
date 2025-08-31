# tests/test_trade_executor.py
import os
import csv
import pytest
from services import trade_executor

@pytest.fixture(autouse=True)
def setup_tmp_log(tmp_path):
    """
    Redirect TRADE_LOG_PATH to a temporary file for all tests.
    Resets LAST_TRADE_TIME before each test.
    """
    trade_executor.TRADE_LOG_PATH = tmp_path / "trade_log.csv"
    trade_executor.LAST_TRADE_TIME = 0
    yield
    # Cleanup if needed
    if os.path.exists(trade_executor.TRADE_LOG_PATH):
        os.remove(trade_executor.TRADE_LOG_PATH)

def test_place_test_order_writes_trade():
    """
    Test that a trade is written to CSV correctly.
    """
    trade_executor.place_test_order("BTCUSDT", "BUY", 0.001)

    # Assert CSV was created
    assert os.path.exists(trade_executor.TRADE_LOG_PATH)

    # Read back contents
    with open(trade_executor.TRADE_LOG_PATH, newline="") as f:
        reader = list(csv.reader(f))

    # Header + 1 trade
    assert reader[0] == ["timestamp", "symbol", "side", "quantity"]
    assert reader[1][1:] == ["BTCUSDT", "BUY", "0.001"]

def test_trade_cooldown_blocks_second_order(caplog):
    """
    Test that a second trade within cooldown is blocked.
    """
    caplog.set_level("WARNING", logger="services.trade_executor")

    # First trade should go through
    trade_executor.place_test_order("BTCUSDT", "BUY", 0.001)
    # Second trade should be blocked due to cooldown
    trade_executor.place_test_order("BTCUSDT", "SELL", 0.002)

    with open(trade_executor.TRADE_LOG_PATH, newline="") as f:
        rows = list(csv.reader(f))

    # Only header + first trade should exist
    assert len(rows) == 2

    # Check that cooldown warning was logged
    assert any("cooldown in effect" in record.getMessage() for record in caplog.records)
