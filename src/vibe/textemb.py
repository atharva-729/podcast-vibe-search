"""Transcript text embeddings (topic signal) + zero-shot prompt vectors, then the final feature table."""
import numpy as np
import pandas as pd

from . import features
from .config import path
from .embed import Gemma


def run():
    seg = pd.read_parquet(path("index") / "segments.parquet")
    tr = pd.read_parquet(path("index") / "transcripts.parquet").set_index("segment_id").loc[seg.segment_id]
    enc = Gemma(text_only=True)
    docs = [f"title: none | text: {t}" if t.strip() else "title: none | text: (no speech)" for t in tr.text]
    np.save(path("index") / "text_emb.npy", enc.text(docs, prompt_name=None))
    prompts = sorted({p for pair in features.ZERO_SHOT.values() for p in pair})
    vecs = enc.text(prompts)
    return features.finalize(dict(zip(prompts, vecs)))
