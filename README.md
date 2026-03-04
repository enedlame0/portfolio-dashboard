# Portfolio Dashboard

Interactive portfolio analytics dashboard built with Python, Dash, Plotly, and yfinance.

## Setup

1. Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install pandas dash plotly yfinance
```

3. Run the app from the project root:

```powershell
python app/app_dash.py
```

4. Open `http://127.0.0.1:8050`.

## `data/holdings.csv`

This CSV is example transaction data used to demonstrate the analytics pipeline.

- It contains buys/sells across multiple tickers.
- Required fields:
  - `transaction_date`
  - `transaction_type` (`purchase`/`sale`)
  - `ticker`
  - `quantity`
  - `currency`
  - `asset_class`
- The current sample is USD-based for portfolio analysis.

## Features

- Portfolio value time series from transaction history and market prices
- Risk metrics: Max Drawdown, historical VaR, historical CVaR
- Allocation views: asset weights and portfolio composition
- Geographic exposure pie chart derived from yfinance metadata
