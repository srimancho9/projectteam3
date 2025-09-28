import re

PII_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',          # SSN
    r'\b\d{3}-\d{3}-\d{4}\b',          # US phone
    r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',  # email
    r'\b\d{5}(?:-\d{4})?\b',           # US ZIP
]

def redact_phi(text: str) -> str:
    out = text
    for p in PII_PATTERNS:
        out = re.sub(p, "[REDACTED]", out)
    return out
