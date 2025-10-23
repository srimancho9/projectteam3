import re
from typing import Dict
ADVICE_DISCLAIMER = ("This is not medical advice. Consult a qualified clinician for decisions about "
                     "diagnosis, treatment, or prevention.")

def sanitize_claim(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:1000]

def safety_checks(claim: str) -> Dict[str, bool]:
    lower = (claim or "").lower()
    emerg = any(x in lower for x in ["suicid", "emergency", "chest pain", "unconscious"])
    pregnancy = "pregnan" in lower
    pedi = any(x in lower for x in ["child", "infant", "toddler", "pediatric"])
    return {"emergency_flag": emerg, "pregnancy_flag": pregnancy, "pediatric_flag": pedi}
