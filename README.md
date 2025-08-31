# TradeForge 

TradeForge is an all-in-one Python-based trading platform that combines real-time market data visualization, technical analysis, ML predictions, strategy backtesting, live charts, and simulated trade execution — all in a user-friendly Streamlit dashboard.

##  Key Features

- Real-time OHLCV data dashboard with multiple timeframes  
- SMA, EMA, RSI, MACD technical indicators  
- ML-based buy/sell signal predictions (RandomForest & XGBoost)  
- Strategy backtesting with portfolio simulation and performance metrics  
- Simulated trade execution with testnet logging  
- Live candlestick charts with auto-refresh  
- Equity curve visualization and buy/sell markers  
- Configurable strategy parameters (RSI thresholds, ML model selection)  
-  Simulated auto-trading toggle with cooldown handling (Testnet support)    
- Centralized logging with color-coded console output and file logs  
- Multi-page modular Streamlit design for easy navigation  

##  Architecture Overview

**Data Layer:**  
- Real-time OHLCV data from SQL database or CSV fallback  
- Labeled datasets for ML predictions  

**Indicator & Analytics Layer:**  
- SMA, EMA, RSI, MACD calculations  
- Signal generation for trading strategies  

**ML Prediction Layer:**  
- RandomForest / XGBoost models for buy/sell predictions  
- Integrated with visualization for marker overlays  

**Backtest Engine:**  
- Strategy simulation with portfolio, metrics, and charts  

**Trade Execution Layer:**  
- Testnet trade placement with logging  
- Cooldown management to prevent rapid orders  

**Visualization Layer:**  
- Candlestick charts with indicators, signals, and equity curve  
- Plotly & Matplotlib integration  

**Config & Logger:**  
- Auto-trading toggle and strategy parameter adjustments via Streamlit  
- Centralized, color-coded logging with emoji indicators  

##  Data

- OHLCV CSV files (e.g., BTCUSDT_15m.csv)  
- ML-labeled CSVs for signal predictions  

##  Tech Stack

- Python 3.13  
- Streamlit (UI)  
- Pandas, NumPy (data processing)  
- Plotly, Matplotlib (charts)  
- scikit-learn 
- Joblib (model serialization)  
- Logging & config management  
- SQL / CSV data sources 
- Random Forest, XG Boost (ML models)

##  How It Works

1. User selects trading pair, interval, and chart settings from the sidebar.  
2. App fetches OHLCV data from SQL database or CSV fallback.  
3. Technical indicators (SMA, EMA, RSI, MACD) are computed.  
4. ML model predicts buy/sell signals and overlays them on charts.  
5. Users can run strategy backtests and view portfolio performance.  
6. Simulated trades can be executed via the Trade Executor page.  
7. Live charts auto-refresh with updated data and predictions.  
8. Strategy parameters and auto-trading status can be configured in Settings.  

## 👤 Contributor

- **Amil Gauri** —  Contributor, Developer, Maintainer  

## 📄 License

This project is open-source under the **MIT License**.  

You are free to use, modify, and distribute it with proper credit.  

See the full license details [here](./LICENSE).
