from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True, "v": "dbg4"}

def _safe_import_playbook():
    try:
        from app.playbook import screen_against_playbook  # normal path
        return screen_against_playbook
    except Exception:
        try:
            from app.config.app.playbook import screen_against_playbook  # nested path (your current layout)
            return screen_against_playbook
        except Exception as e:
            def fallback(data):
                return {
                    "verdict": "ERROR",
                    "setup_grade": "N/A",
                    "position_size": "N/A",
                    "reasons": [f"Playbook import failed: {type(e).__name__}: {e}"],
                    "data_used": data
                }
            return fallback

_screen = _safe_import_playbook()

def _merge(primary: dict, secondary: dict) -> dict:
    out = dict(primary or {})
    for k, v in (secondary or {}).items():
        if out.get(k) in (None, "", 0) and v not in (None, ""):
            out[k] = v
    return out

def _safe_get_prices():
    try:
        from app.providers.prices import get_prices
        return get_prices
    except Exception:
        return lambda _t: {"last_price": None, "float_m": None, "market_cap": None}

def _safe_get_fundamentals():
    try:
        from app.providers.fundamentals import get_fundamentals
        return get_fundamentals
    except Exception:
        return lambda _t: {"inst_pct": None, "insider_pct": None}

def _safe_get_finviz():
    try:
        from app.providers.finviz import get_finviz_data
        return get_finviz_data
    except Exception:
        return lambda _t: {"float_m": None, "insider_pct": None, "inst_pct": None}

@app.get("/screen")
def screen(ticker: str = Query(..., min_length=1)):
    try:
        get_prices = _safe_get_prices()
        get_fundamentals = _safe_get_fundamentals()
        get_finviz = _safe_get_finviz()

        prices = get_prices(ticker)
        fundamentals = get_fundamentals(ticker)
        finviz = get_finviz(ticker)

        data = {**(prices or {}), **(fundamentals or {})}
        data = _merge(data, {"float_m": finviz.get("float_m")})
        data = _merge(data, {"inst_pct": finviz.get("inst_pct"), "insider_pct": finviz.get("insider_pct")})
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
            "ticker": ticker
        })

        # Never crash here—return clear JSON if playbook itself raises
        try:
            return _screen(data)
        except Exception as e:
            return {
                "verdict": "ERROR",
                "setup_grade": "N/A",
                "position_size": "N/A",
                "reasons": [f"Playbook runtime error: {type(e).__name__}: {e}"],
                "data_used": data
            }

    except Exception as e:
        # absolute last resort: still return JSON
        return {
            "verdict": "ERROR",
            "setup_grade": "N/A",
            "position_size": "N/A",
            "reasons": [f"Endpoint error: {type(e).__name__}: {e}"],
            "data_used": {"ticker": ticker}
        }
