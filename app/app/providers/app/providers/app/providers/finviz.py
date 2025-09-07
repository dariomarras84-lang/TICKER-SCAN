try:
    from finvizfinance.quote import finvizfinance
except Exception:
    finvizfinance = None

def get_finviz_data(ticker: str):
    if finvizfinance is None:
        return {"float_m": None, "insider_pct": None, "inst_pct": None}
    try:
        stock = finvizfinance(ticker)
        data = stock.ticker_fundament()

        def num(v):
            if not v: return None
            s = str(v).strip()
            if s.endswith("M"): return float(s[:-1])
            if s.endswith("B"): return float(s[:-1]) * 1000.0
            if s.endswith("%"): return float(s[:-1])
            try: return float(s)
            except Exception: return None

        return {
            "float_m": num(data.get("Shs Float")),
            "insider_pct": num(data.get("Insider Own")),
            "inst_pct": num(data.get("Inst Own"))
        }
    except Exception:
        return {"float_m": None, "insider_pct": None, "inst_pct": None}
