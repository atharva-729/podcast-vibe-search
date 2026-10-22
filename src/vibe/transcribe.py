"""faster-whisper transcripts: one pass per episode window, words assigned to segments by time."""
import json
import os
import time

import pandas as pd

from .audio import decode, raw_file
from .config import ROOT, cfg, model_path, path


def run():
    seg = pd.read_parquet(path("index") / "segments.parquet")
    eps = pd.read_parquet(ROOT / "data" / "episodes.parquet").set_index("episode_id")
    parts = path("index") / "parts" / "whisper"
    parts.mkdir(parents=True, exist_ok=True)

    from faster_whisper import WhisperModel
    m = WhisperModel(model_path("whisper"), device="cpu", compute_type=cfg()["models"]["whisper_compute"],
                     cpu_threads=int(os.environ.get("VIBE_THREADS", 6)))
    t0 = time.time()
    groups = list(seg.groupby("episode_id", sort=False))
    for n, (ep_id, g) in enumerate(groups, 1):
        f = parts / f"{ep_id}_{int(g.start_s.min())}-{int(g.end_s.max())}.json"
        if not f.exists():
            lo, hi = g.start_s.min(), g.end_s.max()
            x = decode(raw_file(eps.loc[ep_id, "audio_file"]), 16000, lo, hi - lo)
            words = []
            for s in m.transcribe(x, language="en", beam_size=1, word_timestamps=True, vad_filter=True)[0]:
                words += [(w.start + lo, w.end + lo, w.word.strip()) for w in (s.words or [])]
            f.write_text(json.dumps(words), encoding="utf-8")
        print(f"[{n}/{len(groups)}] {ep_id} {(time.time() - t0) / 60:.1f} min", flush=True)

    rows = []
    for ep_id, g in groups:
        f = parts / f"{ep_id}_{int(g.start_s.min())}-{int(g.end_s.max())}.json"
        words = json.loads(f.read_text(encoding="utf-8"))
        for r in g.itertuples():
            ws = [w for s, e, w in words if r.start_s <= (s + e) / 2 < r.end_s]
            rows.append({"segment_id": r.segment_id, "text": " ".join(ws), "n_words": len(ws),
                         "pace_wpm": len(ws) / ((r.end_s - r.start_s) / 60)})
    out = pd.DataFrame(rows)
    out.to_parquet(path("index") / "transcripts.parquet", index=False)
    return out
