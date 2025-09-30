# Medical Summarize & Write App

Streamlit app for medical text **Summarization** and **Writing** with evidence hooks and early trust scoring.

## Features
- **Summarize**
  - Paste/upload text or PDF → 5–10 bullets with evidence markers.
  - Metrics: Coverage (ROUGE-L), Evidence coverage, Redundancy, Trust score.
  - AI vs Expert view when abstract is provided.

- **Write**
  - Outline → Expand → Refine (IMRaD, Case Report, Review).
  - Inserts [#] placeholders for claims.
  - PubMed citation resolution (in progress).
  - Export drafts (JSON / TXT / Markdown).

## Quick start

### 1) Install
```bash
pip install -r requirements.txt
```

### 2) Environment
Create `.env`:
```
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
NGROK_AUTH_TOKEN=your_ngrok_token
NCBI_TOOL=med-write-app
NCBI_EMAIL=you@example.com
```

### 3) Run
```bash
streamlit run app.py --server.port 8501 --server.headless true
```

In Colab, the notebook launches Streamlit and prints a public ngrok URL.

## Repo layout
```
app.py                  # Streamlit entry (tabs)
utils/                  # Summarize pipeline (I/O, chunking, embeddings, FAISS, metrics)
write_tab.py            # Write tab UI
write_utils.py          # Document model, prompts, export
write_references.py     # PubMed resolution (WIP)
pubmed_retrieval.py     # PubMed API calls
write_safety.py         # PHI sanitizer (WIP)
requirements.txt
```

## Current results
- Coverage (ROUGE-L): ~0.22
- Evidence coverage: ~1.00
- Redundancy: ~0.01
- Trust score: ~0.6–0.8 (occasional dip to 0.3)

## Status & next steps
- Summarize and Write functional.
- PubMed resolver and Sanitize tab in progress.
- Fact-check bot planned.
- Next milestone: stable PubMed integration, sanitization, baseline benchmarking.
