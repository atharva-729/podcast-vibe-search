"""Decoding and segmenting.

The bundle already holds the first 15 min of each episode in its original codec. We keep
those files as the source and decode on demand at whatever rate a model needs
(16 kHz for EmbeddingGemma 2 and Whisper, 48 kHz for CLAP), so nothing is stored twice.
"""
import subprocess

import numpy as np
import pandas as pd

from .config import ROOT, cfg, path


def raw_file(audio_file):
    return path("audio_cache") / "raw" / audio_file


def probe_duration(file):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(file)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def decode(file, sr=None, start=None, dur=None):
    """Mono float32 samples in [-1, 1]."""
    sr = sr or cfg()["audio"]["sample_rate"]
    cmd = ["ffmpeg", "-nostdin", "-v", "error"]
    if start is not None:
        cmd += ["-ss", str(start)]
    cmd += ["-i", str(file)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    out = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32)


def segment_bounds(duration_s, seg_s, hop_s):
    """Windows of seg_s every hop_s that fit fully; a shorter tail window is dropped."""
    n = int((duration_s - seg_s) // hop_s) + 1 if duration_s >= seg_s else 0
    starts = np.arange(n) * hop_s
    return [(float(s), float(s + seg_s)) for s in starts]


def build_segments(episodes):
    a = cfg()["audio"]
    lo, hi = a.get("window_s", [0, a["trim_minutes"] * 60])
    episodes = episodes.sort_values("pub", ascending=False).groupby("show_id", sort=False).head(
        a.get("index_episodes_per_show", len(episodes)))
    rows = []
    for ep in episodes.itertuples():
        dur = min(probe_duration(raw_file(ep.audio_file)), hi) - lo
        for i, (s, e) in enumerate(segment_bounds(dur, a["segment_s"], a["hop_s"])):
            rows.append({"segment_id": f"{ep.episode_id}_{i:03d}", "episode_id": ep.episode_id,
                         "show_id": ep.show_id, "start_s": s + lo, "end_s": e + lo})
    return pd.DataFrame(rows)


def run():
    episodes = pd.read_parquet(ROOT / "data" / "episodes.parquet")
    seg = build_segments(episodes)
    out = path("index") / "segments.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    seg.to_parquet(out, index=False)
    return seg
