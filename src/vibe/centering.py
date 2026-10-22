"""Closing the modality gap: subtract each modality's mean vector before comparing.

In EmbeddingGemma 2's shared space, text vectors sit closer to other text (mean cosine ~0.69) and audio to other
audio (~0.71) than text to audio (~0.57). Subtracting the audio mean (over the whole catalogue) and a text mean
(over a fixed, neutral phrase set) and re-normalising lines the two clouds up, so single-word queries find the right
clips far more often. Both means are fixed vectors, so at query time this is one subtraction.

The text mean uses GENERIC_PHRASES: everyday sound/voice/setting vocabulary, deliberately not the demo or test
searches, so it can't be tuned to them.
"""
from functools import lru_cache

import numpy as np

from .config import path

GENERIC_PHRASES = [
    "a man talking", "a woman talking", "two people talking", "a group conversation", "an interview", "a monologue",
    "a lecture", "a phone call", "people laughing", "someone crying", "shouting", "whispering", "singing", "humming",
    "applause", "a crowd", "a stadium", "a quiet room", "a busy street", "a cafe", "rain", "wind", "thunder", "birds",
    "ocean waves", "a fire crackling", "traffic", "footsteps", "a door closing", "typing", "piano music",
    "guitar music", "drums", "electronic music", "orchestral music", "jazz", "a radio jingle", "an advertisement",
    "silence", "static noise", "a fast speaker", "a slow speaker", "a deep voice", "a high voice", "an old man",
    "a young child", "an excited voice", "a calm voice", "an angry voice", "a sad voice", "a nervous voice",
    "a confident voice", "a funny story", "a scary story", "a sad story", "a bedtime story", "a news report",
    "a weather report", "a sports commentary", "a cooking show", "a science explanation", "a history lesson",
    "a meditation", "a prayer", "a speech", "a debate", "an argument", "a joke", "gossip", "a recipe", "an audiobook",
    "a podcast intro", "a game show", "a quiz", "a love story", "a crime report", "a business update",
]


def _l2(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True).clip(1e-12)


def compute(audio_emb, encoder):
    """Audio mean over the catalogue + text mean over GENERIC_PHRASES -> index/centering.npz."""
    means = {"audio": audio_emb.mean(0), "text": encoder.text(GENERIC_PHRASES).mean(0)}
    np.savez(path("index") / "centering.npz", **means)
    return means


@lru_cache
def means():
    f = path("index") / "centering.npz"
    if not f.exists():
        return None
    d = np.load(f)
    return {"audio": d["audio"], "text": d["text"]}


def audio(x, strength=1.0):
    """Subtract `strength` × the audio mean (0 = raw, 1 = full centring), then re-normalise."""
    m = means()
    return x if m is None or not strength else _l2(x - strength * m["audio"])


def text(x, strength=1.0):
    m = means()
    return x if m is None or not strength else _l2(x - strength * m["text"])
