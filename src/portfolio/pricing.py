import pandas as pd

def fetch_prices_yfinance(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    import yfinance as yf
    px = yf.download(tickers=tickers, start=start, end=end, auto_adjust=True, progress=False)["Close"]
    if isinstance(px, pd.Series):
        px = px.to_frame()
    px = px.sort_index().dropna(how="all")
    px.columns = [c.upper() for c in px.columns]
    return px


def fetch_ticker_regions_yfinance(tickers: list[str]) -> dict[str, str]:
    import yfinance as yf

    country_to_region = {
        "UNITED STATES": "US",
        "CANADA": "North America",
        "MEXICO": "Latin America",
        "BRAZIL": "Latin America",
        "ARGENTINA": "Latin America",
        "CHILE": "Latin America",
        "COLOMBIA": "Latin America",
        "PERU": "Latin America",
        "UNITED KINGDOM": "Europe",
        "IRELAND": "Europe",
        "FRANCE": "Europe",
        "GERMANY": "Europe",
        "NETHERLANDS": "Europe",
        "SWITZERLAND": "Europe",
        "ITALY": "Europe",
        "SPAIN": "Europe",
        "BELGIUM": "Europe",
        "DENMARK": "Europe",
        "SWEDEN": "Europe",
        "NORWAY": "Europe",
        "FINLAND": "Europe",
        "PORTUGAL": "Europe",
        "AUSTRIA": "Europe",
        "POLAND": "Europe",
        "CZECH REPUBLIC": "Europe",
        "HUNGARY": "Europe",
        "GREECE": "Europe",
        "TURKEY": "Middle East & Africa",
        "ISRAEL": "Middle East & Africa",
        "UNITED ARAB EMIRATES": "Middle East & Africa",
        "SAUDI ARABIA": "Middle East & Africa",
        "SOUTH AFRICA": "Middle East & Africa",
        "EGYPT": "Middle East & Africa",
        "MOROCCO": "Middle East & Africa",
        "NIGERIA": "Middle East & Africa",
        "KENYA": "Middle East & Africa",
        "CHINA": "Asia",
        "HONG KONG": "Asia",
        "TAIWAN": "Asia",
        "JAPAN": "Asia",
        "SOUTH KOREA": "Asia",
        "INDIA": "Asia",
        "SINGAPORE": "Asia",
        "INDONESIA": "Asia",
        "MALAYSIA": "Asia",
        "THAILAND": "Asia",
        "VIETNAM": "Asia",
        "PHILIPPINES": "Asia",
        "PAKISTAN": "Asia",
        "SRI LANKA": "Asia",
        "BANGLADESH": "Asia",
        "AUSTRALIA": "Oceania",
        "NEW ZEALAND": "Oceania",
    }

    out: dict[str, str] = {}
    for ticker in sorted({t.upper() for t in tickers}):
        if ticker == "CASH":
            out[ticker] = "Cash"
            continue
        try:
            tk = yf.Ticker(ticker)
            info = {}
            try:
                info = tk.get_info() or {}
            except Exception:
                # Backward compatibility with yfinance versions without get_info.
                info = tk.info or {}

            country = str(info.get("country") or "").strip().upper()
            region = str(info.get("region") or "").strip()

            if country and country in country_to_region:
                out[ticker] = country_to_region[country]
            elif country:
                out[ticker] = "Other"
            elif region:
                out[ticker] = region
            else:
                out[ticker] = "Other"
        except Exception:
            out[ticker] = "Other"
    return out
