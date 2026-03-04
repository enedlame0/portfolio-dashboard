import pandas as pd

def portfolio_value(holdings: pd.DataFrame, prices: pd.DataFrame, asof_date=None) -> pd.DataFrame:
    if asof_date is None:
        asof_date = pd.Timestamp.today().normalize()
    else:
        asof_date = pd.to_datetime(asof_date).normalize()

    h = holdings.loc[
        holdings["transaction_date"] <= asof_date,
        ["ticker", "transaction_date", "signed_quantity"],
    ].copy()
    if h.empty:
        out = pd.DataFrame(index=prices.index)
        out["portfolio_value"] = 0.0
        out["value_CASH"] = 0.0
        return out

    missing = set(h["ticker"]) - set(prices.columns)
    if missing:
        raise ValueError(f"Missing prices for: {sorted(missing)}")

    # Execute each transaction at the next available market date.
    tx_dates = pd.to_datetime(h["transaction_date"])
    idx = prices.index
    pos = idx.searchsorted(tx_dates, side="left")
    if (pos >= len(idx)).any():
        bad_dates = sorted(pd.to_datetime(tx_dates[pos >= len(idx)]).dt.strftime("%Y-%m-%d").unique())
        raise ValueError(f"Transaction dates are after available price history: {bad_dates}")
    h["effective_date"] = idx[pos]

    share_flows = (
        h.pivot_table(
            index="effective_date",
            columns="ticker",
            values="signed_quantity",
            aggfunc="sum",
            fill_value=0.0,
        )
        .sort_index()
    )

    negative = (share_flows.cumsum() < -1e-9).any()
    if negative.any():
        offenders = sorted(negative[negative].index.tolist())
        raise ValueError(f"Sale exceeds cumulative purchases for: {offenders}")

    positions = share_flows.reindex(prices.index, fill_value=0.0).cumsum()
    positions = positions.reindex(columns=sorted(h["ticker"].unique()), fill_value=0.0)
    values = prices[positions.columns].mul(positions, axis=0).add_prefix("value_")

    tx = h.copy()
    tx["trade_price"] = [
        prices.loc[eff, ticker] for eff, ticker in zip(tx["effective_date"], tx["ticker"])
    ]
    tx["trade_value"] = tx["signed_quantity"] * tx["trade_price"]
    tx["buy_cost"] = tx["trade_value"].where(tx["signed_quantity"] > 0, 0.0)
    tx["sale_proceeds"] = (-tx["trade_value"]).where(tx["signed_quantity"] < 0, 0.0)

    daily_cash = (
        tx.groupby("effective_date")[["buy_cost", "sale_proceeds"]]
        .sum()
        .reindex(prices.index, fill_value=0.0)
    )

    # Cash waterfall:
    # 1) sales increase cash
    # 2) buys consume cash
    # 3) if buys exceed cash, external funding tops up shortfall and cash stays at 0
    cash_levels = []
    external_levels = []
    cash_balance = 0.0
    external_cum = 0.0
    for dt in prices.index:
        cash_balance += float(daily_cash.at[dt, "sale_proceeds"])
        buy_cost = float(daily_cash.at[dt, "buy_cost"])
        if buy_cost <= cash_balance:
            cash_balance -= buy_cost
        else:
            external_cum += (buy_cost - cash_balance)
            cash_balance = 0.0
        cash_levels.append(cash_balance)
        external_levels.append(external_cum)

    cash = pd.Series(cash_levels, index=prices.index)
    values["value_CASH"] = cash

    out = pd.DataFrame(index=values.index)
    out["portfolio_value"] = values.sum(axis=1)
    out["external_funding_cum"] = pd.Series(external_levels, index=prices.index)
    return out.join(values)

def daily_returns(series: pd.Series) -> pd.Series:
    return series.pct_change().dropna()

def weights_latest(values_by_asset: pd.DataFrame) -> pd.Series:
    last = values_by_asset.iloc[-1]
    w = last / last.sum()
    return w.sort_values(ascending=False)
