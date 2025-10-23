from typing import List, Dict
from datetime import datetime

TIER_WEIGHT = {
    "guideline": 4.0, "systematic_review": 3.5, "randomized_trial": 3.0,
    "cohort": 2.0, "case_control": 1.5, "case_series": 1.0,
    "in_vitro": 0.5, "animal": 0.5,
}

def score_item(x: Dict) -> float:
    year = x.get("year") or 0
    try:
        recency = max(0, datetime.now().year - int(year))
    except:
        recency = 10
    tier = x.get("tier", "cohort")
    weight = TIER_WEIGHT.get(tier, 1.0)
    recency_factor = max(0.2, 1.0 - recency / 20.0)
    applicability = x.get("applicability", 1.0)
    oa_boost = 1.1 if (x.get("oa_url") or "").strip() else 1.0
    return weight * recency_factor * (0.5 + 0.5 * applicability) * oa_boost

def rank_items(items: List[Dict]) -> List[Dict]:
    for it in items:
        it["_score"] = score_item(it)
    return sorted(items, key=lambda z: z.get("_score", 0), reverse=True)
