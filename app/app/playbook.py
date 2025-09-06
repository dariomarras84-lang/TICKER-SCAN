{
  "hard_avoid": {
    "float_m_lt": 1.0,
    "inst_pct_gt": 40.0,
    "insider_pct_gt": 60.0,
    "reverse_split_days_lt": 30,
    "cash_runway_months_ge": 12,
    "entry_below_vwap": true,
    "non_gapper": true
  },
  "prefer": {
    "float_m_range": [2, 100],
    "inst_pct_le": 25,
    "insider_pct_lt": 60,
    "cash_runway_months_range": [1, 6],
    "reverse_split_days_ge": 30
  },
  "news_tags": {
    "A_plus": ["no news", "patent", "all stock transaction", "conference", "paid pump"],
    "A": ["fluff", "partnership", "overallotment", "change org"],
    "B": ["new deal", "delisting", "compliance", "test results", "product"],
    "C": ["cancer", "merger", "acquisition", "phase iii", "alzheimer", "billionaire", "top companies", "crypto"]
  },
  "setup_grading": {
    "A_plus": {
      "gap_up_pct_min": 50,
      "gap_up_pct_max": 100,
      "short_before_1030": true,
      "above_vwap_pct_min": 20,
      "above_dilution_pct_min": 15,
      "above_dilution_pct_max": 30,
      "premarket_two_step_window": "04:15-04:45",
      "halt_ok_float_m_ge": 3,
      "paid_pump_or_room": true
    },
    "A": {
      "active_dilution_or_at_level": true,
      "daily_resistance_or_overextension": true,
      "halt_ok_float_m_range": [1, 3]
    },
    "B": {
      "needs_strong_resistance_confirmation": true,
      "no_dilution_but_supporting_confluence": true
    }
  },
  "position_sizing": {
    "float_m_breaks": [
      { "max": 1, "size": "no_trade" },
      { "min": 1, "max": 2, "size": "half" },
      { "min": 2, "size": "full" }
    ],
    "max_shares": 2000,
    "max_dollars": 4000
  }
}
