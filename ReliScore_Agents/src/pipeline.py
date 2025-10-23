from typing import Dict, List, Tuple
from statistics import mean
from .safety import sanitize_claim, safety_checks
from .nlp.claim_detect import classify_intent, query_terms
from .nlp.normalize import normalize_title
from .sources.pubmed import search_pubmed
from .sources.europe_pmc import search_eupmc
from .sources.crossref import search_crossref
from .sources.preprints import search_preprints
from .sources.ctgov import search_ctgov
from .sources.fda import search_fda_oncology
from .sources.fulltext import enrich_oa
from .extract.effects import extract_effects, infer_direction
from .aggregate.prevention import pooled_effect
from .reasoner.verdict import decide_verdict
from .ranking import rank_items
from .graph.build_graph import build_entity_graph, persist_graph, load_graph
from .graph.graphrag import graphrag_retrieve
from .multihop.router import route as route_hops
from .multihop.qa import run_multihop
from .config import load_run_config

CFG = load_run_config()

def _counts(items: List[Dict]) -> Tuple[int,int,int]:
    s = sum(1 for x in items if (x.get("direction") or "").lower()=="supports")
    r = sum(1 for x in items if (x.get("direction") or "").lower()=="refutes")
    u = len(items) - s - r
    return s, r, max(0,u)

def _year_span(items: List[Dict]):
    years = [y for y in (x.get("year") for x in items) if isinstance(y,int)]
    return (min(years), max(years)) if years else (None, None)

def _avg_score(items: List[Dict]) -> float:
    return round(mean([x.get("_score",0) for x in items]) if items else 0.0, 2)

def emit_study_points(items: List[Dict]) -> List[Dict]:
    out = []
    for it in items:
        it["title"] = normalize_title(it.get("title"))
        eff = extract_effects(it.get("abstract","")) or extract_effects(it.get("summary","")) or extract_effects(it.get("title",""))
        if eff: it["effect"] = eff
        it["direction"] = infer_direction(it.get("title",""), it.get("abstract",""), it.get("effect"))
        out.append(it)
    return out

def aggregate(items: List[Dict], intent: str) -> Dict:
    agg = {}
    if intent == "prevention":
        agg["prevention"] = pooled_effect(items)
    return agg

def _top_effect_snippets(items: List[Dict], k: int = 5):
    picks = []
    for it in items:
        e = it.get("effect")
        if isinstance(e, dict) and e.get("value"):
            s = {
                "title": (it.get("title") or "")[:180],
                "year": it.get("year"),
                "metric": e.get("metric"),
                "value": e.get("value"),
                "ci_low": e.get("ci_low"),
                "ci_high": e.get("ci_high"),
                "direction": it.get("direction"),
                "source": it.get("source"),
                "id": it.get("id"),
                "oa_url": it.get("oa_url"),
                "_score": it.get("_score",0),
            }
            picks.append(s)
    picks.sort(key=lambda z: z.get("_score",0), reverse=True)
    return picks[:k]

def build_narrative_facts(claim: str, intent: str, ranked_items: List[Dict], verdict: Dict, aggregates: Dict, hop_trace=None) -> Dict:
    s, r, u = _counts(ranked_items)
    y0, y1 = _year_span(ranked_items)
    avg = _avg_score(ranked_items)
    pooled = (aggregates or {}).get("prevention", {}).get("pooled")
    facts = {
        "claim": claim,
        "intent": intent,
        "verdict": verdict,
        "counts": {"supports": s, "refutes": r, "unclear": u, "total": len(ranked_items)},
        "years": {"earliest": y0, "latest": y1},
        "avg_score": avg,
        "pooled_effect": pooled,
        "top_effects": _top_effect_snippets(ranked_items, k=6),
        "top_titles": [(it.get("year"), (it.get("title") or "")[:180]) for it in ranked_items[:8]],
        "hop_trace": hop_trace or [],
    }
    return facts

def _retrieve_corpus(intent: str, q: dict) -> List[Dict]:
    pools: List[Dict] = []
    if intent == "meta_news":
        pools += search_fda_oncology(q.get("fda",""), n=25)
    pools += search_pubmed(q.get("pubmed",""), n=20)
    pools += search_eupmc(q.get("eupmc",""), n=20)
    pools += search_crossref(q.get("crossref",""), n=10)
    pools += search_preprints(q.get("preprint",""), n=8)
    pools += search_ctgov(q.get("ctgov",""), n=8)
    items = [enrich_oa(x) for x in pools]
    return items

def process_claim(claim_raw: str) -> Dict:
    claim = sanitize_claim(claim_raw)
    sflags = safety_checks(claim)
    intent = classify_intent(claim)
    q = query_terms(claim, intent)
    # Step 1: retrieve
    corpus = _retrieve_corpus(intent, q)
    # Step 2: effects + directions
    study_points = emit_study_points(corpus)
    ranked = rank_items(study_points)
    # Build/Load Graph for Graph-RAG
    g = load_graph()
    if g is None:
        try:
            g = build_entity_graph(ranked)
            persist_graph(g)
        except Exception:
            g = None
    # Router for multi-hop
    hop_mode = route_hops(claim)
    hop_trace = []
    if hop_mode == "multi_hop" and g is not None:
        try:
            mh = run_multihop(g, claim, ranked, hop_limit=CFG.get("multihop",{}).get("hop_limit",3), k=CFG.get("graphrag",{}).get("retriever_k",6))
            hop_trace = mh.get("hop_trace",[])
            # augment ranked with any spans as pseudo-items (for visibility)
            for sp in (mh.get("graph_snippets") or [])[:5]:
                ranked.append({
                    "id": sp.get("source_id","graph"),
                    "source": "GraphRAG",
                    "title": sp.get("title",""),
                    "year": sp.get("year"),
                    "tier": "case_series",
                    "applicability": 0.7,
                    "oa_url": sp.get("oa_url",""),
                    "abstract": sp.get("text",""),
                    "direction": "unclear",
                    "_score": 1.0
                })
            ranked = rank_items(ranked)
        except Exception:
            pass
    # Reason
    verdict = decide_verdict(ranked, intent=intent)
    aggregates = {"prevention": pooled_effect(ranked)} if intent == "prevention" else {}
    facts = build_narrative_facts(claim, intent, ranked, verdict, aggregates, hop_trace=hop_trace)
    return {
        "claim": claim,
        "intent": intent,
        "safety": sflags,
        "study_points": ranked,
        "aggregates": aggregates,
        "verdict": verdict,
        "facts": facts,
        "router_debug": {"mode": hop_mode}
    }