"""Config loading and repo paths."""
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _merge(base, over):
    for k, v in over.items():
        base[k] = _merge(base.get(k, {}), v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return base


@lru_cache
def cfg():
    """config.yaml, overridden by config.local.yaml if present (machine-specific, not committed, e.g. the LLM URL)."""
    c = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    local = ROOT / "config.local.yaml"
    if local.exists():
        _merge(c, yaml.safe_load(local.read_text(encoding="utf-8")) or {})
    return c


def path(key):
    """Repo-relative path from the `paths` section, as an absolute Path."""
    return ROOT / cfg()["paths"][key]


def model_path(key):
    return str(ROOT / cfg()["models"][key])
