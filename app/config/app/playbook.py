from typing import Dict, Any, List, Optional
import json
from pathlib import Path

# Find your criteria JSON no matter where it is
def _find_criteria_path() -> Path:
    here = Path(__file__).resolve()
    candidates = [
        # common location: app/config/playbook_criteria.json (when playbook is app/playbook.py)
        here.parent.parent / "playbook_criteria.json",
        here.parent / "playbook_criteria.json",                      # app/config/playbook_criteria.json
        here.parents[2] / "playbook_criteria.json",                  # app/playbook_criteria.json
        here.parents[3] / "app" / "playbook_criteria.json",          # fallback
    ]
    for p in candidates:
        if p.exists():
            return p
    # last resort: return a non-existing path; loader will handle
    return candidates[0]

CONFIG_PATH = _find_criteria_path()

def _cfg() -> Dict[str, Any]:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _reason(ok: bool, text: str) -> Optional[str]:
    return None if ok else text

def _grade_news(headlines: List[str], tags: Dict[str, List[str]]) -> Dict[str, str]:
    txt = " ".join((headlines or [])).lower()
    for t in tags.get("C", []):
        if t in txt: return {"grade": "C", "hit": t}
    for t in tags.get("B", []):
        if t in txt: return {"grade": "B", "hit": t}
    for t in tags.get("A", []):
        if t in txt: return {"grade": "A", "hit": t}
    for t in tags.get("A_plus", []):
        if t in txt: return {"grade": "A+", "hit": t}
    return {"grade": "A+", "hit": "no news"} if not headlines else {"grade": "A", "hit": "neutral"}

def _position_size(float_m: Optional[float], breaks: List[Dict[str, Any]]) -> str:
    if float_m is None:
        return "half"
    for br in breaks:
        mi, mx, sz = br.get("min"), br.get("max"), br["size"]
        if (mi is None or float_m >= mi) and (mx is None or float_m < mx):
            return sz
    return "half"

def screen_against_playbook(data: Dict[str, Any]) -> Dict[str, Any]:
    c = _cfg()
    hard = c.get("hard_avoid", {})
    pref = c.get("prefer", {})
    news_tags = c.get("news_tags", {})
    pos = c.get("position_sizing", {})

    f = lambda k, d=None: data.get(k, d)

    reasons: List[str] = []
    verdict = "TRADE"
    setup = "A"

    # Hard avoids (any failure -> EXCLUDE)
    reasons += list(filter(None, [
        _reason(not (f("float_m") is not None and f("float_m") < hard.get("float_m_lt", -1)), f"Float < {hard.get('float_m_lt')}M"),
        _reason(not (f("inst_pct") is not None and f("inst_pct") > hard.get("inst_pct_gt", 1e9)), f"Institutional > {hard.get('inst_pct_gt')}%"),
        _reason(not (f("insider_pct") is not None and f("insider_pct") > hard.get('insider_pct_gt', 1e9)), f"Insider > {hard.get('insider_pct_gt')}%"),
        _reason(not (f("reverse_split_days") is not None and f("reverse_split_days") < hard.get("reverse_split_days_lt", -1)), f"Reverse split < {hard.get('reverse_split_days_lt')}d"),
        _reason(not (f("cash_runway_months") is not None and f("cash_runway_months") >= hard.get("cash_runway_months_ge", 1e9)), f"Cash runway ≥ {hard.get('cash_runway_months_ge')}m"),
        _reason(not f("entry_below_vwap"), "Entry below VWAP"),
        _reason(not f("non_gapper"), "Non Gapper")
    ]))
    if any(reasons):
        verdict = "EXCLUDE"

    # Preferences (positive notes)
    if f("float_m") is not None and f("float_m") >= pref.get("float_m_range", [2, 100])[0]:
        reasons.append("Float OK (≥2M)")
    if f("inst_pct") is not None and f("inst_pct") <= pref.get("inst_pct_le", 25):
        reasons.append(f"Institutional ≤ {pref.get('inst_pct_le')}% (ideal)")
    if f("insider_pct") is not None and f("insider_pct") < pref.get("insider_pct_lt", 60):
        reasons.append("Insider < 60% (OK)")
    if f("cash_runway_months") is not None:
        lo, hi = pref.get("cash_runway_months_range", [1, 6])
        if lo <= f("cash_runway_months") <= hi:
            reasons.append(f"Cash runway {lo}-{hi}m (best)")
    if f("reverse_split_days") is not None and f("reverse_split_days") >= pref.get("reverse_split_days_ge", 30):
        reasons.append("Reverse split age OK (≥30d)")

    # News grade
    ng = _grade_news(f("headlines", []), news_tags)
    reasons.append(f"News grade: {ng['grade']} ({ng['hit']})")
    if ng["grade"] == "C":
        verdict = "EXCLUDE"

    size = _position_size(f("float_m"), pos.get("float_m_breaks", []))

    return {
        "verdict": verdict,
        "setup_grade": setup,
        "position_size": size,
        "reasons": [r for r in reasons if r],
        "data_used": data
    }
