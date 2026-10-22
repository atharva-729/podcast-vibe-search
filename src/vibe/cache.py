"""Tiny on-disk JSON cache keyed by a hash of the request."""
import hashlib
import json

from .config import path


def _file(namespace, key):
    digest = hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:24]
    return path("runs") / "cache" / namespace / f"{digest}.json"


def get(namespace, key):
    f = _file(namespace, key)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def put(namespace, key, value):
    f = _file(namespace, key)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return value
