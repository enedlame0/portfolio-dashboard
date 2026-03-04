import pandas as pd

def max_drawdown(value: pd.Series) -> float:
    peak = value.cummax()
    dd = value / peak - 1.0
    return float(dd.min())

def historical_var(returns: pd.Series, alpha: float = 0.05) -> float:
    return float(-returns.quantile(alpha))

def historical_cvar(returns: pd.Series, alpha: float = 0.05) -> float:
    q = returns.quantile(alpha)
    tail = returns[returns <= q]
    return float(-tail.mean())