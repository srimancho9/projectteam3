from typing import List, Dict
import matplotlib.pyplot as plt

def beeswarm_like(study_points: List[Dict]):
    xs = [i for i,_ in enumerate(study_points)]
    ys = [s.get("_score",0) for s in study_points]
    fig, ax = plt.subplots(figsize=(6,3))
    ax.scatter(xs, ys, alpha=0.8)
    ax.set_xlabel("Study rank")
    ax.set_ylabel("Score")
    ax.set_title("Evidence Beeswarm (score vs rank)")
    return fig

def forest_plot(study_points: List[Dict]):
    effs, labels = [], []
    for s in study_points[:15]:
        e = s.get("effect")
        if e and e.get("value"):
            effs.append((e["value"], e.get("ci_low"), e.get("ci_high")))
            labels.append((s.get("title") or s.get("id",""))[:40])
    if not effs:
        fig, ax = plt.subplots(figsize=(6,2))
        ax.text(0.5,0.5,"No extractable effects",ha="center",va="center"); ax.axis("off")
        return fig
    fig, ax = plt.subplots(figsize=(7,0.4*len(effs)+1))
    y = list(range(len(effs)))
    vals = [v for v, lo, hi in effs]
    los = [lo if lo else v for v, lo, hi in effs]
    his = [hi if hi else v for v, lo, hi in effs]
    ax.errorbar(vals, y, xerr=[[v-l for v,l in zip(vals,los)], [h-v for v,h in zip(vals,his)]], fmt='o', capsize=3)
    ax.axvline(1.0, linestyle="--")
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.set_xlabel("Effect ratio (RR/OR/HR)")
    ax.invert_yaxis(); ax.set_title("Forest Plot")
    return fig

def timeline(study_points: List[Dict]):
    pts = [(s.get("year"), s.get("_score",0)) for s in study_points if s.get("year")]
    pts = sorted(pts)
    if not pts:
        fig, ax = plt.subplots(figsize=(6,2))
        ax.text(0.5,0.5,"No dates available",ha="center",va="center"); ax.axis("off")
        return fig
    xs = [x for x,_ in pts]; ys = [y for _,y in pts]
    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(xs, ys, marker="o")
    ax.fill_between(xs, [y*0.9 for y in ys], [y*1.1 for y in ys], alpha=0.2)
    ax.set_xlabel("Year"); ax.set_ylabel("Score"); ax.set_title("Evidence Timeline")
    return fig
