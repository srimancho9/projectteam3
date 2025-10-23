from typing import Any
from .utils import save_json, load_json, sha1, cache_path

def get_or_set(name: str, builder) -> Any:
    p = cache_path(name)
    obj = load_json(p)
    if obj is not None:
        return obj
    obj = builder()
    save_json(p, obj)
    return obj

def memoize_json(key: str, fn, *args, **kwargs) -> Any:
    h = sha1(key)
    p = cache_path(f"memo/{h}.json")
    obj = load_json(p)
    if obj is not None:
        return obj
    obj = fn(*args, **kwargs)
    save_json(p, obj)
    return obj
