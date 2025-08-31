# api/exchange_api.py

import requests
from utils.tradeforge_logger import setup_logger

# Initialize logger for this module
logger = setup_logger(__name__)

def get_all_symbols():
    """
    Fetch all available trading symbols from Binance exchange.
    Returns:
        list: A list of symbol strings (e.g., ['BTCUSDT', 'ETHUSDT'])
    """
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        symbols = [s["symbol"] for s in data.get("symbols", [])]
        logger.info(f"Fetched {len(symbols)} symbols.")
        return symbols
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching trading pairs: {e}")
        return []

def get_current_price(symbol="BTCUSDT"):
    """
    Get the latest market price for the specified trading symbol.
    Parameters:
        symbol (str): Trading pair symbol (default is 'BTCUSDT').
    Returns:
        float or None: The latest price as a float, or None on failure.
    """
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        price = float(response.json().get("price"))
        logger.info(f"Fetched current price for {symbol}: {price}")
        return price
    except (requests.exceptions.RequestException, ValueError, TypeError) as e:
        logger.error(f"Error fetching current price for {symbol}: {e}")
        return None

def fetch_ohlcv(symbol="BTCUSDT", interval="1m", limit=100):
    """
    Fetch historical OHLCV (Open, High, Low, Close, Volume) candlestick data from Binance.
    Parameters:
        symbol (str): Trading pair (e.g., 'BTCUSDT').
        interval (str): Timeframe interval (e.g., '1m', '5m', '1h').
        limit (int): Number of candlesticks to fetch.
    Returns:
        list of dict: OHLCV data in dictionary format with timestamps.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()

        ohlcv = [{
            "timestamp": candle[0],
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5])
        } for candle in raw_data]

        logger.info(f"Fetched {len(ohlcv)} candles for {symbol} [{interval}]")
        return ohlcv

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {symbol}: {e}")
    except (ValueError, TypeError) as ve:
        logger.error(f"Failed to process OHLCV data for {symbol}: {ve}")
    except Exception as ex:
        logger.error(f"Unexpected error in fetch_ohlcv: {ex}")
    
    return []
