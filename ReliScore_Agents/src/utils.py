import os, time, json, hashlib, re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import requests
from loguru import logger

HTTP_TIMEOUT = int(os.environ.get("HTTP_TIMEOUT", "15"))
DATA_DIR = Path.cwd() / "data_cache"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def cache_path(name: str) -> Path:
    return DATA_DIR / name

def save_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def load_json(path: Path) -> Optional[Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None

def get(url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Tuple[Optional[requests.Response], Optional[str]]:
    try:
        res = requests.get(url, params=params, headers=headers, timeout=HTTP_TIMEOUT)
        if res.status_code == 200:
            return res, None
        return None, f"HTTP {res.status_code} for {url}"
    except Exception as e:
        return None, str(e)

def redact_email(text: str) -> str:
    return re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[redacted-email]", text or "")

def dedupe_list(items):
    seen = set()
    out = []
    for x in items:
        try:
            k = json.dumps(x, sort_keys=True, default=str)
        except Exception:
            k = str(x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out

def safe_int(x, default=None):
    try:
        return int(x)
    except:
        return default

def now_ts() -> int:
    return int(time.time())

def log_idempotent(path: Path, key: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    existing = set(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    if key in existing:
        return False
    with path.open("a", encoding="utf-8") as f:
        f.write(key + "\n")
    return True
