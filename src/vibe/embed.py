"""Shared audio-text embeddings. Two backends behind one interface:

  gemma: EmbeddingGemma 2 (16 kHz, whole 20 s segment, 768-d)
  clap:  LAION-CLAP htsat-unfused (48 kHz, max 10 s input -> mean of two 10 s halves, 512-d)

All outputs are L2-normalised float32.
"""
import time

import numpy as np
import pandas as pd
import torch

from .audio import decode, raw_file
from .config import ROOT, cfg, model_path, path

import os

torch.set_num_threads(int(os.environ.get("VIBE_THREADS", torch.get_num_threads())))


def _l2(x):
    x = np.asarray(x, dtype=np.float32)
    return x / np.linalg.norm(x, axis=-1, keepdims=True).clip(1e-12)


class Gemma:
    name, sr = "gemma", 16000

    def __init__(self, text_only=False):
        from sentence_transformers import SentenceTransformer
        drop = {"vision_config": None, **({"audio_config": None} if text_only else {})}
        # float32: bf16 is ~12x slower on CPUs without native support; fp16 gives NaNs (model card).
        self.m = SentenceTransformer(model_path("embed_a"), device="cpu", config_kwargs=drop,
                                     model_kwargs={"dtype": torch.float32})

    def text(self, texts, prompt_name="SearchQuery"):
        return _l2(self.m.encode(list(texts), prompt_name=prompt_name, batch_size=32))

    def audio(self, clips):
        return _l2(self.m.encode([{"array": c, "sampling_rate": self.sr} for c in clips], batch_size=4))


class Clap:
    name, sr = "clap", 48000
    window_s = 10

    def __init__(self):
        from transformers import ClapModel, ClapProcessor
        self.m = ClapModel.from_pretrained(model_path("embed_b")).eval()
        self.p = ClapProcessor.from_pretrained(model_path("embed_b"))

    @staticmethod
    def _out(x):
        return x.pooler_output if hasattr(x, "pooler_output") else x

    @torch.inference_mode()
    def text(self, texts, prompt_name=None):
        inp = self.p(text=list(texts), return_tensors="pt", padding=True)
        return _l2(self._out(self.m.get_text_features(**inp)).numpy())

    @torch.inference_mode()
    def audio(self, clips):
        w = self.window_s * self.sr
        # Deterministic fixed windows instead of the processor's random truncation.
        wins = [c[i:i + w] for c in clips for i in range(0, max(len(c) - w // 2, 1), w)]
        counts = [len(range(0, max(len(c) - w // 2, 1), w)) for c in clips]
        inp = self.p(audio=wins, sampling_rate=self.sr, return_tensors="pt")
        e = _l2(self._out(self.m.get_audio_features(**inp)).numpy())
        out, i = [], 0
        for n in counts:
            out.append(e[i:i + n].mean(0))
            i += n
        return _l2(out)


BACKENDS = {"gemma": Gemma, "clap": Clap}


def load(name):
    return BACKENDS[name]()


def segment_clips(segments, sr):
    """Decode each episode once and slice out its segments, preserving input order."""
    episodes = pd.read_parquet(ROOT / "data" / "episodes.parquet").set_index("episode_id")
    clips = [None] * len(segments)
    for ep_id, g in segments.reset_index(drop=True).groupby("episode_id"):
        x = decode(raw_file(episodes.loc[ep_id, "audio_file"]), sr)
        for i, row in g.iterrows():
            clips[i] = x[int(row.start_s * sr):int(row.end_s * sr)]
    return clips


def embed_segments(model, segments, batch=8, log_every=200):
    """Embeddings in segments' row order, plus seconds spent in the model (excludes decoding)."""
    clips = segment_clips(segments, model.sr)
    out, spent = [], 0.0
    for i in range(0, len(clips), batch):
        t = time.time()
        out.append(model.audio(clips[i:i + batch]))
        spent += time.time() - t
        if log_every and (i // batch) % max(1, log_every // batch) == 0:
            print(f"  {model.name}: {i + batch}/{len(clips)} ({spent:.0f}s)", flush=True)
    return np.concatenate(out), spent


def embed_all(name):
    """Full index, resumable per episode under index/parts/<name>/."""
    seg = pd.read_parquet(path("index") / "segments.parquet")
    parts = path("index") / "parts" / name
    parts.mkdir(parents=True, exist_ok=True)
    model = load(name)
    t0, done = time.time(), 0
    for n, (ep_id, g) in enumerate(seg.groupby("episode_id", sort=False)):
        f = parts / f"{ep_id}_{int(g.start_s.min())}-{int(g.end_s.max())}.npy"
        if not f.exists():
            e, _ = embed_segments(model, g, log_every=0)
            np.save(f, e)
            done += len(g)
        el = time.time() - t0
        print(f"[{n + 1}/{seg.episode_id.nunique()}] {ep_id}: {len(g)} segs, {el / 60:.0f} min elapsed", flush=True)
    emb = np.concatenate([np.load(parts / f"{ep}_{int(g.start_s.min())}-{int(g.end_s.max())}.npy")
                          for ep, g in seg.groupby("episode_id", sort=False)])
    assert len(emb) == len(seg)
    np.save(path("index") / "audio_emb.npy", _l2(emb))
    return emb.shape, time.time() - t0, done
