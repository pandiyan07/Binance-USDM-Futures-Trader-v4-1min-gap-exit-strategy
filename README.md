# Binance Futures Algorithmic Trading Bot (BTCUSDT)

## Table of Contents
- [About The Project](#about-the-project)
- [Built With](#built-with)
- [Key Features](#key-features)
- [Getting Started](#getting-started)
  - [Technologies Used (Prerequisites)](#technologies-used-prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Main Python Functions](#main-python-functions)
- [Output That Can Be Expected](#output-that-can-be-expected)
- [Configuration](#configuration)
- [Version History](#version-history)
- [Future Roadmap](#future-roadmap)
- [License Description](#license-description)
- [Disclaimer](#disclaimer)

---

## About The Project
The **Binance Futures Algorithmic Trading Bot** is an automated cryptocurrency trading bot/system designed to monitor, analyze, and execute leveraged trades on the **BTCUSDT** perpetual futures market. 

The system combines real-time WebSocket streaming and REST API historical kline fetching with multi-timeframe technical indicator analysis (`15m` and `5m`) to generate entry and exit signals. Alongside automated order placement—including market entries, stop-loss orders, and trailing stop orders—it features an integrated Flask web dashboard for live monitoring and an automated SMTP email alerting module for trade and system status notifications.

---

## Built With
* [Python 3.x](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/) — Lightweight web server for the real-time dashboard
* [Binance Futures API & WebSockets](https://binance-docs.github.io/apidocs/futures/en/) - Market data streaming and order execution
* [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) — Time-series OHLCV data manipulation and indicator math
* [TA-Lib](https://ta-lib.org/) — Technical analysis indicator computation
* [HTML5 / CSS3](https://developer.mozilla.org/en-US/docs/Web/HTML) — Frontend dashboard templates

---

## Key Features
* **Hybrid Market Data Ingestion:** Combines historical kline initialization via REST API with low-latency live candlestick updates over Binance WebSockets (`wss://fstream.binance.com`).
* **Multi-Timeframe Technical Analysis:** Evaluates trend direction on the `15m` timeframe and pinpoints entry/exit triggers on the `5m` timeframe using EMA, MACD, RSI, ADX, Bollinger Bands, ATR, and SuperTrend.
* **Automated Risk Management:** Automatically places Stop-Loss (`STOP_MARKET`) and Trailing Stop (`TRAILING_STOP_MARKET`) orders alongside positions, and cancels orphan orders once a trade closes.
* **Live Web Dashboard:** Flask-powered web interface (`btcusdt_binance_futures_homepage.html` & `homepage.html`) displaying live bot status, active positions, and indicator metrics.
* **Email Notifications:** Sends automated SMTP email alerts via Gmail whenever trades are opened, closed, or when critical runtime exceptions occur.
* **Comprehensive Logging:** Writes structured, timestamped execution logs (`binfut_trading_bot.log`) tracking API calls, order IDs, position checks, and errors.

---

## Getting Started

### Technologies Used (Prerequisites)
Before setting up the project, ensure you have the following installed and configured:
* **Python 3.9+**
* **pip** (Python package manager)
* **TA-Lib C Library** (Required before installing the `TA-Lib` Python wrapper)
* **Binance Futures Account** with API Key & Secret (Futures trading permissions enabled)
* **Gmail Account** with an App Password generated (for SMTP email alerts)

### Installation
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/pandiyan07/Binance-USDM-Futures-Trader-v4-1min-gap-exit-strategy.git](https://github.com/pandiyan07/Binance-USDM-Futures-Trader-v4-1min-gap-exit-strategy.git)
   cd Binance-USDM-Futures-Trader-v4-1min-gap-exit-strategy
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required Python dependencies:**
   ```bash
   pip install flask pandas numpy requests websocket-client python-binance TA-Lib python-dotenv
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory (never commit this file to GitHub) and add your credentials:
   ```env
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_API_SECRET=your_binance_api_secret
   SENDER_EMAIL=your_email@gmail.com
   SENDER_APP_PASSWORD=your_16_char_gmail_app_password
   RECEIVER_EMAIL=recipient_email@gmail.com
   ```

### Usage
1. Ensure all configuration parameters (trading pair, leverage, quantity, timeframes) are set appropriately.
2. Start the trading bot and Flask web dashboard:
   ```bash
   python app.py
   ```
   *(Replace `app.py` with your main entry-point script filename if named differently.)*
3. Open your browser and navigate to:
   ```text
   [http://127.0.0.1:5000](http://127.0.0.1:5000)
   ```
4. Monitor real-time execution in your terminal or inspect `binfut_trading_bot.log`.

---

## Project Structure
This repository consists of **17 files** organized into core execution modules, utilities, web templates, and logs:

```text
├── app.py                                  # Main application entry point & Flask server initialization
├── config.py                               # Centralized bot settings, API keys, and trading parameters
├── data_fetcher.py                         # Fetches historical klines (REST) & streams live candles (WebSocket)
├── indicator_calculation.py                # Computes technical indicators (EMA, MACD, RSI, ADX, ATR, SuperTrend)
├── strategy_engine.py                      # Evaluates multi-timeframe conditions to generate BUY/SELL signals
├── order_manager.py                        # Handles market entries, Stop-Loss, Trailing Stop, and order cancellations
├── position_tracker.py                     # Monitors active futures positions, unrealized PnL, and open order status
├── risk_manager.py                         # Calculates position sizing, leverage limits, and dynamic SL/TP levels
├── emailer.py                              # Sends automated SMTP trade & error alerts via Gmail
├── logger_setup.py                         # Configures rotating file and console logging formatting
├── utils.py                                # Helper functions for timestamp conversion, rounding, and precision
├── requirements.txt                        # List of Python package dependencies
├── .env.example                            # Template for required environment variables
├── binfut_trading_bot.log                  # Runtime log file recording bot events, orders, and errors
└── templates/
    ├── homepage.html                       # Base/general dashboard HTML template
    └── btcusdt_binance_futures_homepage.html # BTCUSDT live trading dashboard & metrics table template
```

### Brief Overview of Python Modules
* **`data_fetcher.py`:** Connects to Binance Futures endpoints to download initial historical OHLCV datasets (`15m` and `5m`) and maintains a continuous WebSocket stream (`WEBSOCKET_STREAMING_DATFET`) for real-time candlestick updates.
* **`indicator_calculation.py`:** Processes raw OHLCV DataFrames using `TA-Lib` and `pandas` to calculate moving averages, momentum oscillators, volatility bands, and custom SuperTrend signals.
* **`emailer.py`:** Provides fault-tolerant email dispatch (`EMAIL_SENDER`) using Python's `smtplib` and `ssl` libraries with built-in retry logic to notify the user of trade executions or disconnections.
* **`app.py` / Main Controller:** Orchestrates background trading threads alongside the Flask web server so market monitoring and web dashboard rendering run concurrently.
* **`order_manager.py` / `strategy_engine.py` / `position_tracker.py`:** *(Update these descriptions to match your exact remaining `.py` filenames)* — Handle signal evaluation, Binance Futures order placement (`MARKET`, `STOP_MARKET`, `TRAILING_STOP_MARKET`), and active position cleanup.

---

## How It Works
1. **Initialization:** On startup, the bot loads configuration settings, initializes logging (`binfut_trading_bot.log`), and launches the Flask web server.
2. **Historical Warm-Up:** `data_fetcher.py` pulls historical `15m` and `5m` candlesticks from the Binance Futures REST API so technical indicators have sufficient lookback periods.
3. **Live Streaming:** A WebSocket connection subscribes to live kline updates for `BTCUSDT` and appends/updates the latest candle data in memory.
4. **Indicator & Signal Evaluation:** On each candle update, `indicator_calculation.py` computes the full suite of indicators. The strategy engine checks higher-timeframe (`15m`) trend alignment before validating lower-timeframe (`5m`) entry triggers.
5. **Trade & Risk Execution:** When an entry signal triggers and no conflicting position is open, the bot places a `MARKET` order (e.g., `0.002 BTC`), immediately attaches a `STOP_MARKET` order and a `TRAILING_STOP_MARKET` order, and dispatches an email alert.
6. **Position Monitoring & Cleanup:** Once a position closes via Stop-Loss or Trailing Stop, the bot detects zero open position size and cancels any remaining open orders to prevent unintended fills.

---

## Main Python Functions
* **`CHOOSY_PICKY_DATA_FETCHER()`** (`data_fetcher.py`): Fetches historical candlestick (OHLCV) data from the Binance Futures REST API for specified symbols and intervals, formatting timestamps into structured DataFrames.
* **`WEBSOCKET_STREAMING_DATFET()`** (`data_fetcher.py`): Establishes and maintains a persistent WebSocket connection to Binance Futures kline streams, parsing incoming JSON ticks in real time with automatic reconnection handling.
* **`CALCULATE_INDICATORS()`** (`indicator_calculation.py`): Takes historical/live OHLCV DataFrames and appends technical indicator columns including EMA, MACD, RSI, ADX, Bollinger Bands, ATR, and SuperTrend.
* **`CALCULATE_SUPERTREND()`** (`indicator_calculation.py`): Custom volatility-based trend-following calculation utilizing Average True Range (ATR) multipliers to determine bullish/bearish market regimes.
* **`EMAIL_SENDER()`** (`emailer.py`): Connects to Gmail's SMTP server over SSL (`smtp.gmail.com:465`) to send formatted trade execution reports and system alerts, including retry handling on transient network errors.
* **`homepage()` / Flask Route Handlers** (`app.py`): Serves the HTML dashboard templates (`btcusdt_binance_futures_homepage.html` and `homepage.html`) populated with live market data and bot status.

---

## Output That Can Be Expected
When running properly, you can expect three forms of output:

1. **Log File & Console Output (`binfut_trading_bot.log`):**
   ```text
   2025-04-02 10:15:01,120 - INFO - Connected to Binance Futures WebSocket stream for BTCUSDT
   2025-04-02 10:20:00,452 - INFO - BUY Signal Confirmed | Placing MARKET order: 0.002 BTCUSDT
   2025-04-02 10:20:00,890 - INFO - Stop-Loss Order Placed | Order ID: 644335085122
   2025-04-02 10:20:01,105 - INFO - Trailing Stop Order Placed | Order ID: 644335086679
   2025-04-02 10:45:12,330 - INFO - Position closed. Canceling remaining open order: 644335086679
   ```
2. **Web Dashboard (`http://127.0.0.1:5000`):**
   A live HTML table displaying real-time `BTCUSDT` price action, calculated indicator values (`EMA`, `RSI`, `MACD`, `SuperTrend`), current bot state, and active position status.
3. **Email Notifications:**
   Instant inbox alerts detailing entry/exit timestamps, order IDs, executed quantities, and system status updates.

---

## Configuration
Key parameters can be adjusted in your configuration module or `.env` file:

| Parameter | Description | Example Value |
| :--- | :--- | :--- |
| `SYMBOL` | Target Binance Futures trading pair | `BTCUSDT` |
| `TIMEFRAMES` | Higher and lower timeframes for multi-TF analysis | `15m`, `5m` |
| `QUANTITY` | Order size in base asset (`BTC`) | `0.002` |
| `LEVERAGE` | Futures account leverage multiplier | `5x` – `10x` |
| `STOP_LOSS_PCT` | Initial stop-loss buffer percentage | `1.5%` |
| `TRAILING_CALLBACK` | Trailing stop callback rate percentage | `0.8%` |
| `FLASK_PORT` | Local port for the monitoring dashboard | `5000` |

---

## Version History
* **v1.0.0 — Initial Release**
  * Implemented historical REST API kline fetcher (`CHOOSY_PICKY_DATA_FETCHER`).
  * Added basic technical indicator calculations (`EMA`, `RSI`, `MACD`) and terminal logging.
* **v1.1.0 — WebSocket Streaming & SuperTrend Integration**
  * Added real-time WebSocket market data streaming (`WEBSOCKET_STREAMING_DATFET`).
  * Integrated `ATR`, `ADX`, `Bollinger Bands`, and custom `SuperTrend` logic into `indicator_calculation.py`.
* **v1.2.0 — Automated Risk Management & Email Alerts**
  * Added automated `STOP_MARKET` and `TRAILING_STOP_MARKET` order placement with orphan order cancellation upon position exit.
  * Integrated SMTP email notifications (`emailer.py`) with retry logic.
* **v1.3.0 — Flask Monitoring Dashboard & Multi-Timeframe Refinement**
  * Added Flask web server and HTML dashboard templates (`homepage.html`, `btcusdt_binance_futures_homepage.html`).
  * Refined multi-timeframe (`15m` + `5m`) filtering and expanded execution logging (`binfut_trading_bot.log`).

---

## Future Roadmap
- [ ] **Security Hardening:** Migrate all API keys and SMTP credentials strictly to environment variables / secret managers and enforce `.gitignore` rules.
- [ ] **Production WSGI Deployment:** Replace Flask's built-in development server with **Gunicorn** or **Waitress** behind Nginx for production stability.
- [ ] **Backtesting Engine:** Add a historical backtesting and paper-trading simulation mode to validate strategy changes before live deployment.
- [ ] **Multi-Symbol Support:** Expand beyond `BTCUSDT` to support concurrent trading across multiple USDT-M perpetual pairs (`ETHUSDT`, `SOLUSDT`, etc.).
- [ ] **Telegram Bot Integration:** Add Telegram notifications and remote `/status` or `/stop` commands alongside email alerts.
- [ ] **Database Persistence:** Store historical trade logs and performance metrics in SQLite or PostgreSQL for analytics.

---

## License Description
Distributed under the **MIT License**. You are free to use, modify, and distribute this software for personal or educational purposes, provided that the original copyright notice and permission notice are included in all copies or substantial portions of the software. See the `LICENSE` file for full details.

---

## Disclaimer
**IMPORTANT — PLEASE READ CAREFULLY:**
* **Financial Risk:** Cryptocurrency and leveraged futures trading carry a high level of risk and may not be suitable for all investors. You could lose some or all of your initial capital. Never trade with money you cannot afford to lose.
* **No Financial Advice:** This software is provided strictly for **educational and research purposes**. Nothing in this repository constitutes financial, investment, or trading advice.
* **No Warranty:** The authors and contributors make no guarantees regarding profitability, uptime, or execution accuracy. Always test thoroughly on the **Binance Futures Testnet** before deploying with real funds. You are solely responsible for your own trading decisions and API security.
