from typing import List, Dict, Tuple, Optional
import math
from statistics import mean

def _counts(study_points: List[Dict]) -> Dict[str,int]:
    supp = sum(1 for s in study_points if (s.get("direction") or "").lower()=="supports")
    refu = sum(1 for s in study_points if (s.get("direction") or "").lower()=="refutes")
    uncl = len(study_points) - supp - refu
    return {"supports": supp, "refutes": refu, "unclear": max(0, uncl)}

def _years_and_scores(study_points: List[Dict]) -> Tuple[list, list]:
    pts = [(s.get("year"), s.get("_score",0)) for s in study_points if s.get("year")]
    pts = sorted(pts)
    if not pts: return [], []
    xs = [x for x,_ in pts]; ys = [y for _,y in pts]
    return xs, ys

def _slope(xs: list, ys: list) -> Optional[float]:
    n = len(xs)
    if n < 2: return None
    xbar = sum(xs)/n; ybar = sum(ys)/n
    num = sum((x-xbar)*(y-ybar) for x,y in zip(xs,ys))
    den = sum((x-xbar)**2 for x in xs) or 1e-9
    return num/den

def _effects(study_points: List[Dict]):
    vals = []
    for s in study_points:
        e = s.get("effect")
        if isinstance(e, dict) and isinstance(e.get("value"), (int,float)) and e["value"]>0:
            vals.append(e["value"])
    return vals

def insights(study_points: List[Dict], verdict: Dict) -> Dict:
    n = len(study_points); counts = _counts(study_points)
    consensus = (counts["supports"] / n) if n>0 else 0.0
    xs, ys = _years_and_scores(study_points)
    trend = _slope(xs, ys)
    effs = _effects(study_points); has_fx = len(effs) > 0
    if has_fx:
        log_vals = [math.log(v) for v in effs if v>0]
        med_log = sorted(log_vals)[len(log_vals)//2] if log_vals else 0.0
    else:
        med_log = 0.0
    avg_score = mean([s.get("_score",0) for s in study_points]) if n else 0.0
    label = (verdict or {}).get("label","Unclear")
    return {"n": n, "supports": counts["supports"], "refutes": counts["refutes"], "unclear": counts["unclear"],
            "consensus": consensus, "avg_score": avg_score, "trend_slope": trend, "has_effects": has_fx,
            "median_log_effect": med_log, "label": label}

def captions_from_insights(ins: Dict) -> Dict[str, str]:
    if ins["n"] == 0: reli_take = "No evidence found to split."
    else:
        if ins["supports"] > ins["refutes"]:
            reli_take = f"Evidence leans supportive ({ins['supports']} vs {ins['refutes']})."
        elif ins["refutes"] > ins["supports"]:
            reli_take = f"Evidence leans against the claim ({ins['refutes']} vs {ins['supports']})."
        else:
            reli_take = "Support and refutation are balanced."
    reli_why = "A larger supportive portion raises confidence; a larger refuting portion lowers it."
    reli_how = "Segments show proportions that support, refute, or are unclear."

    tc_take = f"Consensus ≈ {ins['consensus']:.2f} with average quality ≈ {ins['avg_score']:.2f}."
    if ins["label"] == "Supported": tc_take += " Studies cluster toward agreement."
    elif ins["label"] == "Contradicted": tc_take += " Studies cluster toward disagreement."
    elif ins["label"] == "Mixed": tc_take += " Agreement is split."

    if ins["trend_slope"] is None: tl_take = "Not enough dated studies to assess trends."
    elif ins["trend_slope"] > 0.01: tl_take = "Evidence quality trends upward over time."
    elif ins["trend_slope"] < -0.01: tl_take = "Evidence quality trends downward over time."
    else: tl_take = "Evidence quality is relatively stable over time."
    tl_how = "Line shows average study score by year; band shows a simple range."
    tl_why = "Upward trends suggest growing confidence; downward trends suggest weakening support."

    if not ins["has_effects"]: eg_take = "Few studies reported effect sizes; points may cluster near zero."
    else:
        if ins["median_log_effect"] < 0: eg_take = "Reported effects tilt toward risk reductions (ratios < 1)."
        elif ins["median_log_effect"] > 0: eg_take = "Reported effects tilt toward risk increases (ratios > 1)."
        else: eg_take = "Reported effects cluster near no change."
    eg_how = "x=year, y=quality, z≈log(effect)."
    eg_why = "Stronger departures from zero hint at stronger effects."

    return {
        "reli_graph": f"**Takeaway:** {reli_take}\n*How to read:* {reli_how}\n*Why it matters:* {reli_why}",
        "trust_compass": f"**Takeaway:** {tc_take}\n*How to read:* Right = agreement, Up = quality.\n*Why it matters:* Position reflects how aligned and strong the evidence is.",
        "timeline_ribbon": f"**Takeaway:** {tl_take}\n*How to read:* {tl_how}\n*Why it matters:* {tl_why}",
        "evidence_galaxy": f"**Takeaway:** {eg_take}\n*How to read:* {eg_how}\n*Why it matters:* {eg_why}",
    }
