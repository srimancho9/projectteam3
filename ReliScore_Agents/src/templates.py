from typing import List, Dict

def format_citation(item: Dict) -> str:
    year = item.get("year") or "n.d."
    src = item.get("source", "Unknown")
    title = (item.get("title", "Untitled") or "").strip()
    ident = item.get("id", "")
    return f"[{src} {year}] {title} ({ident})"

def build_citations_markdown(study_points: List[Dict], limit: int = None) -> str:
    items = study_points if limit is None else study_points[:max(0, limit)]
    lines = [f"- {format_citation(c)}" for c in items]
    return "\n".join(lines) if lines else "_No citations available._"

def build_reasons_markdown(verdict: Dict) -> str:
    rs = (verdict or {}).get("reasons") or []
    if not rs:
        return "_No key reasons extracted._"
    return "\n".join(f"- {r}" for r in rs)
