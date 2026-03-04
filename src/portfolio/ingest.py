import pandas as pd

def load_holdings(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["transaction_date"])
    required = {
        "transaction_date",
        "transaction_type",
        "ticker",
        "quantity",
        "currency",
        "asset_class",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Holdings missing columns: {missing}")

    df["ticker"] = df["ticker"].astype(str).str.upper()
    tx_raw = df["transaction_type"].astype(str).str.strip().str.lower()
    mapping = {"purchase": "purchase", "buy": "purchase", "sale": "sale", "sell": "sale"}
    df["transaction_type"] = tx_raw.map(mapping)
    if df["transaction_type"].isna().any():
        bad = sorted(tx_raw[df["transaction_type"].isna()].unique())
        raise ValueError(f"Invalid transaction_type values: {bad}. Use purchase/sale.")

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    if df["quantity"].isna().any() or (df["quantity"] <= 0).any():
        raise ValueError("quantity must be numeric and > 0 for all rows.")

    sign = df["transaction_type"].map({"purchase": 1.0, "sale": -1.0})
    df["signed_quantity"] = df["quantity"] * sign
    return df
