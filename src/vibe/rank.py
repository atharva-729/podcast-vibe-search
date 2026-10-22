"""Hybrid ranking: vibe_sim (query text vs segment audio) + feature_fit + topic_sim, with explanations."""
from functools import lru_cache

import numpy as np
import pandas as pd

from . import centering
from .config import ROOT, cfg, path
from .features import FEATURES

LEVEL = {"low": 0.2, "mid": 0.5, "high": 0.8}
MIN_TOPIC_WORDS = 15
WORDS = {  # feature -> (low words, high words)
    "energy": ("low energy", "high energy"), "expressiveness": ("flat delivery", "expressive voices"),
    "pace_wpm": ("slow pace", "fast pace"), "pause_ratio": ("few pauses", "lots of pauses"),
    "music_score": ("no music", "music"), "laughter_score": ("no laughter", "lots of laughter"),
    "crowd_score": ("no crowd", "crowd noise"),
}


@lru_cache
def index():
    seg = pd.read_parquet(path("index") / "segments.parquet")
    eps = pd.read_parquet(ROOT / "data" / "episodes.parquet")
    feats = pd.read_parquet(path("index") / "features.parquet")
    df = seg.merge(eps[["episode_id", "show", "title", "category", "vibe", "audio_url"]], on="episode_id") \
            .merge(feats, on="segment_id")
    assert list(df.segment_id) == list(seg.segment_id)
    return df, np.load(path("index") / "audio_emb.npy"), np.load(path("index") / "text_emb.npy")


def center_strength(override=None):
    """How much of the modality gap to close: 0 = raw embeddings, 1 = full centring (config `rank.center`)."""
    if override is not None:
        return float(override)
    c = cfg()["rank"].get("center", 0)
    return 1.0 if c is True else float(c or 0)


@lru_cache
def audio_for_text_search(strength=None):
    """Audio embeddings as compared against text queries, centred by `strength` (see center_strength)."""
    _, audio, _ = index()
    return centering.audio(audio, center_strength(strength))


def query_vec(texts, strength=None):
    """Text query embedding(s) for text-to-audio search, centred to match audio_for_text_search()."""
    return centering.text(encoder().text(texts), center_strength(strength))


@lru_cache
def encoder():
    from .embed import Gemma
    return Gemma(text_only=True)


def minmax(x):
    lo, hi = x.min(), x.max()
    return (x - lo) / (hi - lo) if hi > lo else np.zeros_like(x)


def feature_fit(df, targets, avoid=()):
    terms = [1 - np.abs(df[f + "_pct"].to_numpy() - LEVEL[v]) for f, v in targets.items()]
    for a in avoid:
        f, _, v = a.partition(":")
        terms.append(np.abs(df[f + "_pct"].to_numpy() - LEVEL[v]))
    return np.mean(terms, axis=0) if terms else np.zeros(len(df))


def describe(row, targets, topic_n=None, topic=None):
    """Plain-words reasons from the numbers: matched targets first, else the segment's most extreme features."""
    parts = []
    if targets:
        fits = sorted(((1 - abs(row[f + "_pct"] - LEVEL[v]), f, v) for f, v in targets.items()), reverse=True)
        parts = [WORDS[f][v == "high"] if v != "mid" else f"medium {WORDS[f][1].split()[-1]}"
                 for fit, f, v in fits if fit >= 0.75][:3]
    if not parts:
        ext = sorted(((abs(row[f + "_pct"] - 0.5), f) for f in FEATURES), reverse=True)
        parts = [WORDS[f][int(row[f + "_pct"] > 0.5)] for d, f in ext if d >= 0.35][:3]
    if topic and topic_n is not None and topic_n >= 0.6:
        parts.append(f"topic: {topic}")
    return parts


def select(df, score, k, max_per_show, exclude=()):
    """Top-k with at most max_per_show per show; neighbours of a picked segment are merged into it."""
    order = np.argsort(-score)
    picked, per_show, taken = [], {}, set(exclude)
    for i in order:
        r = df.iloc[i]
        key = (r.episode_id, r.start_s)
        if i in taken or per_show.get(r.show_id, 0) >= max_per_show:
            continue
        if any(p_ep == r.episode_id and abs(p_s - r.start_s) <= cfg()["audio"]["segment_s"] for p_ep, p_s in
               ((df.iloc[j].episode_id, df.iloc[j].start_s) for j in picked)):
            continue
        picked.append(i)
        per_show[r.show_id] = per_show.get(r.show_id, 0) + 1
        taken.add(i)
        if len(picked) == k:
            break
    return picked


def score_all(q, weights=None, parsed=None, strength=None):
    """Score every segment for a query: (parsed, score, vibe_n, fit, topic_n)."""
    from .query import parse
    df, audio, text = index()
    w = weights or {"vibe": cfg()["rank"]["w_vibe"], "feature": cfg()["rank"]["w_feature"],
                    "topic": cfg()["rank"]["w_topic"]}
    p = parsed or parse(q)
    enc = encoder()
    # The user's own words plus the LLM's (often long) sound description; long text alone embeds poorly.
    qv = query_vec([q, p["vibe_text"]], strength).sum(0)
    vibe_n = minmax(audio_for_text_search(strength) @ (qv / np.linalg.norm(qv)))
    fit = feature_fit(df, p["targets"], p["avoid"])
    topic_n = np.zeros(len(df))
    if p["topic"]:
        # Near-silent segments have empty transcripts that all share one embedding; they get no topic score.
        topic_n = minmax(text @ enc.text([p["topic"]])[0]) * (df.n_words.to_numpy() >= MIN_TOPIC_WORDS)
    w_t = w["topic"] if p["topic"] else 0.0
    w_f = w["feature"] if (p["targets"] or p["avoid"]) else 0.0
    return p, w["vibe"] * vibe_n + w_f * fit + w_t * topic_n, vibe_n, fit, topic_n


def search(q, k=5, weights=None, max_per_show=None, parsed=None, strength=None):
    df, _, _ = index()
    p, score, vibe_n, fit, topic_n = score_all(q, weights, parsed, strength)
    picked = select(df, score, k, max_per_show or cfg()["rank"]["max_per_show"])
    return p, [result(df.iloc[i], score[i], {"vibe": vibe_n[i], "feature": fit[i], "topic": topic_n[i]},
                      describe(df.iloc[i], p["targets"], topic_n[i], p["topic"])) for i in picked]


def nearest_clips(text, k=25, strength=None):
    """Row indices of the k clips whose audio embedding is closest to the text: the embedding alone, nothing else."""
    return [int(i) for i in np.argsort(-(audio_for_text_search(strength) @ query_vec([text], strength)[0]))[:k]]


def like(segment_id, k=5, w_audio=0.6, w_feat=0.4, max_per_show=None, exclude_neighbours=True):
    """More like this: audio-embedding similarity + feature closeness. No LLM."""
    df, audio, _ = index()
    i = int(np.flatnonzero(df.segment_id.to_numpy() == segment_id)[0])
    a = minmax(audio @ audio[i])
    pct = df[[f + "_pct" for f in FEATURES]].to_numpy()
    f = 1 - np.abs(pct - pct[i]).mean(1)
    score = w_audio * a + w_feat * f
    seed = df.iloc[i]
    excl = {i}
    if exclude_neighbours:
        excl |= set(np.flatnonzero((df.episode_id == seed.episode_id).to_numpy()
                                   & (np.abs(df.start_s.to_numpy() - seed.start_s) <= cfg()["audio"]["segment_s"])))
    picked = select(df, score, k, max_per_show or 10 ** 6, exclude=excl)
    return [result(df.iloc[j], score[j], {"audio": a[j], "feature": f[j]}, describe(df.iloc[j], {})) for j in picked]


def result(r, score, parts, why):
    return {"segment_id": r.segment_id, "show": r.show, "show_id": r.show_id, "episode": r.title,
            "category": r.category, "vibe": r.vibe, "start_s": float(r.start_s), "end_s": float(r.end_s),
            "audio_url": r.audio_url, "score": round(float(score), 3),
            "parts": {k: round(float(v), 3) for k, v in parts.items()}, "why": why}
