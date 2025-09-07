try:
    import yfinance as yf
except Exception:
    yf = None

def get_prices(ticker: str):
    if yf is None:
        return {"last_price": None, "float_m": None, "market_cap": None}
    try:
        t = yf.Ticker(ticker)
        fast = dict(getattr(t, "fast_info", {}) or {})
        info = dict(getattr(t, "info", {}) or {})
        last_price = fast.get("last_price") or info.get("regularMarketPrice")
        market_cap = info.get("marketCap")
        float_shares = info.get("floatShares")
        float_m = float(float_shares) / 1_000_000.0 if float_shares else None
        return {"last_price": last_price, "float_m": float_m, "market_cap": market_cap}
    except Exception:
        return {"last_price": None, "float_m": None, "market_cap": None}
