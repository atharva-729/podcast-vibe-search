"""Per-segment sound features -> index/features.parquet.

Acoustic (librosa, from audio): energy mean/variance, expressiveness (pitch spread), pause ratio.
From transcripts: pace_wpm. Zero-shot from the shared space: music / laughter / crowd scores.
Every feature also gets a 0-1 percentile within the corpus (`<name>_pct`).
"""
import librosa
import numpy as np
import pandas as pd

from .audio import decode, raw_file
from .config import ROOT, path

SR, FRAME, HOP = 16000, 1024, 512
SILENCE_DB = 25   # frame is a pause if this far below the episode's loud level (p95)
VOICED_DB = 15    # frames this close to the loud level are used for pitch

# (positive, contrast) prompt per score. Laughter and crowd contrast speech with speech: against plain
# "people talking", any non-speech audio (ASMR, nature) scored as laughter/crowd. These pairs were picked
# by checking per-vibe means (comedy should be highest on laughter) - light tuning on weak labels.
ZERO_SHOT = {
    "music_score": ("music playing", "people talking"),
    "laughter_score": ("a group of friends laughing out loud at a joke", "a person speaking seriously"),
    "crowd_score": ("a live audience laughing and applauding", "a quiet studio recording"),
}

FEATURES = ["energy", "expressiveness", "pace_wpm", "pause_ratio", "music_score", "laughter_score", "crowd_score"]


def frame_db(x):
    rms = librosa.feature.rms(y=x, frame_length=FRAME, hop_length=HOP)[0]
    return 20 * np.log10(rms + 1e-10)


def acoustic(x, ref_db):
    """Features for one segment of 16 kHz mono audio, given the episode's loud level."""
    db = frame_db(x)
    silent = db < ref_db - SILENCE_DB
    active = db[~silent] if (~silent).any() else db
    out = {"energy_mean": float(active.mean()), "energy_var": float(active.std()),
           "pause_ratio": float(silent.mean())}
    f0 = librosa.yin(x, fmin=70, fmax=400, sr=SR, frame_length=FRAME * 2, hop_length=HOP)
    n = min(len(f0), len(db))
    f0 = f0[:n][db[:n] > ref_db - VOICED_DB]
    if len(f0) > 10:
        semi = 12 * np.log2(f0)
        semi = semi[np.abs(semi - np.median(semi)) < 12]  # drop octave errors
        out["expressiveness"] = float(semi.std()) if len(semi) > 10 else np.nan
    else:
        out["expressiveness"] = np.nan
    return out


def run_acoustic():
    seg = pd.read_parquet(path("index") / "segments.parquet")
    eps = pd.read_parquet(ROOT / "data" / "episodes.parquet").set_index("episode_id")
    rows = []
    for ep_id, g in seg.groupby("episode_id", sort=False):
        lo, hi = g.start_s.min(), g.end_s.max()
        x = decode(raw_file(eps.loc[ep_id, "audio_file"]), SR, lo, hi - lo)
        ref = np.percentile(frame_db(x), 95)
        for r in g.itertuples():
            clip = x[int((r.start_s - lo) * SR):int((r.end_s - lo) * SR)]
            rows.append({"segment_id": r.segment_id, **acoustic(clip, ref)})
    out = pd.DataFrame(rows)
    out.to_parquet(path("index") / "acoustic.parquet", index=False)
    return out


def zero_shot(audio_emb, prompt_emb):
    """prompt_emb: dict prompt text -> unit vector, for every prompt in ZERO_SHOT."""
    return {k: audio_emb @ prompt_emb[pos] - audio_emb @ prompt_emb[neg] for k, (pos, neg) in ZERO_SHOT.items()}


def percentile(s):
    return s.rank(pct=True, method="average").fillna(0.5)


def finalize(prompt_emb):
    seg = pd.read_parquet(path("index") / "segments.parquet")
    ac = pd.read_parquet(path("index") / "acoustic.parquet")
    tr = pd.read_parquet(path("index") / "transcripts.parquet")
    emb = np.load(path("index") / "audio_emb.npy")
    df = seg[["segment_id"]].merge(ac, on="segment_id").merge(tr[["segment_id", "pace_wpm", "n_words"]], on="segment_id")
    for k, v in zero_shot(emb, prompt_emb).items():
        df[k] = v
    # "energy" combines loudness and its variation: calm = quiet and steady.
    df["energy"] = (percentile(df.energy_mean) + percentile(df.energy_var)) / 2
    for f in FEATURES:
        df[f + "_pct"] = percentile(df[f])
    df.to_parquet(path("index") / "features.parquet", index=False)
    return df
