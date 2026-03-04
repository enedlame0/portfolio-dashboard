# Portfolio Dashboard (Python + Dash)

An interactive portfolio analytics dashboard built with Python, Dash, Plotly, and yfinance.
It ingests transaction-level holdings, reconstructs historical positions, computes portfolio/risk metrics, and visualizes performance and allocation.

## What This Project Shows

- End-to-end portfolio analytics workflow from transactions to dashboard.
- Time-series portfolio valuation based on market data.
- Risk metrics and allocation analysis suitable for interview/project discussion.
- Presentation-ready dashboard design for investor-style reporting.

## Setup and Run

### 1. Prerequisites

- Python 3.10+ (tested on Python 3.13)
- Internet connection (required for yfinance market/metadata calls)

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install pandas plotly dash yfinance
```

### 4. Run the dashboard

From the project root:
>>>>>>> c768c5dda7269f23e6fa6d2a3fefd0f0125cbb8d

```powershell
python app/app_dash.py
```

Then, the dashboard server should automatically open. If the user's browser permissions do not allow for this, then run:

`http://127.0.0.1:8050`

## Holdings File (`data/holdings.csv`)

`data/holdings.csv` is an example transaction ledger used to demonstrate the analytics pipeline.
It is not meant to represent real personal holdings.

### Expected columns

- `transaction_date`: trade date (YYYY-MM-DD)
- `transaction_type`: `purchase` or `sale`
- `ticker`: market symbol (uppercased by ingestion)
- `quantity`: positive trade quantity
- `currency`: currently `USD` for all sample rows
- `asset_class`: label used for grouping/context

### Notes on the sample data

- Includes US, European, and Asian large-cap names (using USD-listed tickers/ADRs where relevant).
- The dashboard computes signed quantities from transaction type (`purchase` = +, `sale` = -).
- All analytics are expressed in USD in this sample setup.

## Dashboard Features

- KPI cards:
  - Portfolio Value
  - P/L vs Contributions
  - Return on Invested Capital
  - Max Drawdown
  - Historical VaR (5%)
  - Historical CVaR (5%)
- Charts:
  - Portfolio Value Trend (area chart)
  - Daily Returns Distribution (box plot)
  - Current Asset Weights (bar chart)
  - Portfolio Composition (donut chart)
  - Geographical Exposure (donut chart, inferred via yfinance metadata)

## Project Structure

```text
app/
  app_dash.py                 # Dash app and visualization layer
data/
  holdings.csv                # Example transaction data
src/portfolio/
  ingest.py                   # Holdings ingestion and validation
  pricing.py                  # Market data + ticker metadata (yfinance)
  analytics.py                # Portfolio valuation and weights
  risk.py                     # Risk metrics (MDD, VaR, CVaR)
tests/
```

## Troubleshooting

- `ModuleNotFoundError: No module named 'src'`
  - Run from the project root using `python app/app_dash.py`.
- New transactions do not appear:
  - Restart the Dash server; CSV edits are not always hot-reloaded.
- yfinance errors or missing metadata:
  - Check your internet connection and retry.
  - Some tickers may map to `Other` if metadata is unavailable.
