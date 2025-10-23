from typing import List, Dict
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import math

def _split_counts(study_points: List[Dict]):
    by_src = {}
    dir_map = {"supports":0, "refutes":0, "unclear":0}
    for s in study_points:
        src = s.get("source","Other") or "Other"
        by_src[src] = by_src.get(src,0) + 1
        d = (s.get("direction") or "unclear").lower()
        if d not in dir_map: d = "unclear"
        dir_map[d] += 1
    return by_src, dir_map

def reli_graph(study_points: List[Dict]):
    _, dir_map = _split_counts(study_points)
    total = sum(dir_map.values()) or 1
    parts = [dir_map.get("supports",0)/total, dir_map.get("refutes",0)/total, dir_map.get("unclear",0)/total]
    labels = ["Supports","Refutes","Unclear"]
    fig, ax = plt.subplots(figsize=(7,1.8))
    left = 0.0
    for frac, lab in zip(parts, labels):
        ax.barh([0], [frac], left=left)
        if frac > 0: ax.text(left + frac/2, 0, f"{lab} {int(frac*100)}%", va="center", ha="center")
        left += frac
    ax.set_xlim(0,1); ax.set_yticks([])
    ax.set_title("ReliGraph — Evidence Split (Stacked)")
    ax.set_xlabel("Proportion of study points")
    return fig

def trust_compass(study_points: List[Dict]):
    n = max(1, len(study_points))
    supp = sum(1 for s in study_points if (s.get("direction") or "").lower()=="supports")
    consensus = supp / n
    quality = sum(s.get("_score",0) for s in study_points)/n
    fig, ax = plt.subplots(figsize=(5,4))
    ax.scatter([consensus],[quality], s=200)
    ax.set_xlim(0,1); ax.set_ylim(0, max(1, quality*1.5))
    ax.set_xlabel("Consensus (0..1)"); ax.set_ylabel("Quality (score)")
    ax.set_title("Trust Compass")
    return fig

def timeline_ribbon(study_points: List[Dict]):
    pts = [(s.get("year"), s.get("_score",0)) for s in study_points if s.get("year")]
    pts = sorted(pts)
    if not pts:
        fig, ax = plt.subplots(figsize=(6,2))
        ax.text(0.5,0.5,"No dates available",ha="center",va="center"); ax.axis("off")
        return fig
    xs = [x for x,_ in pts]; ys = [y for _,y in pts]
    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(xs, ys, marker="o")
    ax.fill_between(xs, [y*0.85 for y in ys], [y*1.15 for y in ys], alpha=0.2)
    ax.set_xlabel("Year"); ax.set_ylabel("Score"); ax.set_title("Evidence Timeline Ribbon")
    return fig

def _safe_effect_value(s: Dict):
    e = s.get("effect")
    if isinstance(e, dict): return e.get("value")
    return None

def evidence_galaxy_3d(study_points: List[Dict]):
    xs, ys, zs, cs = [], [], [], []
    for s in study_points:
        y = s.get("year"); ifnot = y is None
        if not y: continue
        xs.append(y); ys.append(s.get("_score",0))
        eff = _safe_effect_value(s)
        try: z = math.log(eff) if isinstance(eff,(int,float)) and eff and eff > 0 else 0.0
        except Exception: z = 0.0
        zs.append(z); cs.append(s.get("applicability",1.0))
    fig = plt.figure(figsize=(7,4)); ax = fig.add_subplot(111, projection='3d')
    if not xs:
        ax.text2D(0.5,0.5,"No 3D points", transform=ax.transAxes); return fig
    ax.scatter(xs, ys, zs, s=40, alpha=0.9, c=cs)
    ax.set_xlabel("Year"); ax.set_ylabel("Quality (score)"); ax.set_zlabel("log(effect)")
    ax.set_title("Evidence Galaxy (3D)")
    return fig
