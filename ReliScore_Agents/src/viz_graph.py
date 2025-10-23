from typing import Dict
import matplotlib.pyplot as plt
import networkx as nx
import io, base64

def draw_neighborhood(neighborhood: Dict, out_path: str) -> str:
    nodes = neighborhood.get("nodes") or []
    edges = neighborhood.get("edges") or []
    if not nodes:
        fig, ax = plt.subplots(figsize=(4,2))
        ax.text(0.5,0.5,"No neighborhood",ha="center",va="center"); ax.axis("off")
        fig.savefig(out_path, bbox_inches="tight"); plt.close(fig)
        return out_path
    g = nx.Graph()
    g.add_nodes_from(nodes)
    for u,v,rel in edges:
        g.add_edge(u,v,rel=rel)
    pos = nx.spring_layout(g, seed=42, k=0.6)
    fig, ax = plt.subplots(figsize=(5,4))
    nx.draw_networkx_nodes(g, pos, node_size=300, ax=ax)
    nx.draw_networkx_labels(g, pos, font_size=8, ax=ax)
    nx.draw_networkx_edges(g, pos, alpha=0.6, ax=ax)
    ax.axis("off")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path
