from utils.llm_client import LLMClient

def write_research_paragraph(topic: str, refs_hint: str = "") -> str:
    sys = "You are a research writer. Produce a coherent, neutral, factual paragraph with clear structure."
    usr = f"Write one ~200-word paragraph on: {topic}.\nIf relevant, mention methods or evaluation. {refs_hint}"
    return LLMClient().complete(sys, usr)
