import json, os
from pathlib import Path

DEFAULTS = {
    "graphrag": {"retriever_k": 6, "hops": 2},
    "multihop": {"hop_limit": 3},
    "sd": {"model_id": "runwayml/stable-diffusion-v1-5", "height": 512, "width": 512, "steps": 25, "guidance": 7.5},
    "agent": {"max_hops": 3, "enable_calculator": True, "allow_images": True},
}

def load_json_if_exists(p: str):
    try:
        fp = Path(p)
        if fp.exists():
            return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def load_run_config():
    cfg = DEFAULTS.copy()
    cfg.update(load_json_if_exists("/mnt/data/Week7_run_config.json"))
    env_cfg = load_json_if_exists("/mnt/data/Week7-env_week7.json")
    if env_cfg:
        cfg["env"] = env_cfg
    return cfg
