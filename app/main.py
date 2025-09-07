from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

# Try to import your playbook wherever it lives
def _get_playbook():
    try:
        # standard location: app/playbook.py
        from app.playbook import screen_against_playbook
        return screen_against_playbook
    except Exception:
        try:
            # your current nested location: app/config/app/playbook.py
            from app.config.app.playbook import screen_against_playbook
            return screen_against_playbook
        except Exception:
            # last-resort fallback: noop playbook
            def fallback(data):
                return {
                    "verdict": "ERROR",
                    "setup_grade": "N/A",
                    "position_size": "N/A",
                    "reasons": ["Playbook not found/import failed"],
                    "data_used": data,
                }
            return fallback

_screen = _get_playbook()

def _merge(primary: dict, secondary: dict) -> dict:
    out = dict(primary or {})
    for k, v in (secondary or {}).items():
        if out.get(k) in (None, "", 0) and v not in (None, ""):
            out[k] = v
    return out

@app.get("/screen")
def screen(ticker: str = Query(..., min_length=1)):
    # lazy imports keep startup safe even if providers fail
    try:
        from app.providers.prices import get_prices
    except Exception:
        def get_prices(_): return {"last_price": None, "float_m": None, "market_cap": None}
    try:
        from app.providers.fundamentals import get_fundamentals
    except Exception:
        def get_fundamentals(_): return {"inst_pct": None, "insider_pct": None}
    try:
        from app.providers.finviz import get_finviz_data
    except Exception:
        def get_finviz_data(_): return {"float_m": None, "insider_pct": None, "inst_pct": None}

    prices = get_prices(ticker)
    fundamentals = get_fundamentals(ticker)
    finviz = get_finviz_data(ticker)

    data = {**(prices or {}), **(fundamentals or {})}
    data = _merge(data, {"float_m": finviz.get("float_m")})
    data = _merge(data, {"inst_pct": finviz.get("inst_pct"), "insider_pct": finviz.get("insider_pct")})

    # placeholders you can connect later
    data.update({
        "reverse_split_days": None,
        "cash_runway_months": None,
        "price_above_vwap_pct": None,
        "above_dilution_pct": None,
        "gap_up_pct": None,
        "is_halt_play": None,
        "is_paid_pump": None,
        "headlines": [],
        "entry_below_vwap": False,
        "non_gapper": False,
        "ticker": ticker,
    })

    return _screen(data)
