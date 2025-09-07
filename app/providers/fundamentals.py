# Yahoo Finance: ownership (safe fallback)
try:
    import yfinance as yf
except Exception:
    yf = None

def get_fundamentals(ticker: str):
    if yf is None:
        return {"inst_pct": None, "insider_pct": None}
    try:
        t = yf.Ticker(ticker)
        info = dict(getattr(t, "info", {}) or {})
        inst = info.get("heldPercentInstitutions")
        ins = info.get("heldPercentInsiders")
        inst_pct = float(inst) * 100.0 if inst is not None else None
        insider_pct = float(ins) * 100.0 if ins is not None else None
        return {"inst_pct": inst_pct, "insider_pct": insider_pct}
    except Exception:
        return {"inst_pct": None, "insider_pct": None}
