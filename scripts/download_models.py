"""Download all model weights into the local cache (models/). Safe to rerun."""
import sys
import time
from pathlib import Path

import truststore

truststore.inject_into_ssl()  # use the Windows cert store (corporate TLS inspection)

import yaml
from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
cache = ROOT / cfg["paths"]["models"]

repos = [
    cfg["models"]["embed_a"],
    cfg["models"]["embed_b"],
    f"Systran/faster-whisper-{cfg['models']['whisper']}",
]
for repo in repos:
    t = time.time()
    path = snapshot_download(repo, cache_dir=cache)
    size = sum(f.stat().st_size for f in Path(path).rglob("*") if f.is_file()) / 1e6
    print(f"{repo}: {size:.0f} MB in {time.time() - t:.0f}s -> {path}", flush=True)
print("done", file=sys.stderr)
