"""Study: how much of the modality gap should search close?

Variants are centring strengths (0 = raw embeddings, 1 = full centring; see centering.py). Each variant's top 4
clips per search are judged by a listener (docs/rate.html?queue=study). Ratings are pooled across all listening
files, so a (search, clip) pair is only ever rated once.

  study A: the 12 demo searches (long, descriptive) at strengths 0, .25, .5, .75, 1
  study B: 10 short searches (one or two words) at strengths 0, .5, 1
The automatic category check is also run at each strength, to compare the two measures.
"""
import json
import random

import numpy as np

from . import rank
from .config import ROOT, path
from .evaluate import CATEGORY_QUERIES, DEMO_QUERIES

STUDIES = {
    "long": {"queries": DEMO_QUERIES, "strengths": [0, 0.25, 0.5, 0.75, 1]},
    "short": {"queries": ["laughter", "music", "sports", "news", "calm", "whispering", "rain", "crime",
                          "a children's story", "football"], "strengths": [0, 0.5, 1]},
}
TOP_K = 4
RATING_FILES = ["listening_test_v1.json", "listening_test_centred.json", "listening_study.json"]


def all_ratings():
    out = {}
    for name in RATING_FILES:
        f = path("reports") / name
        if f.exists():
            out.update(json.loads(f.read_text(encoding="utf-8"))["ratings"])
    return out


def design():
    """Top-K clip ids for every (study, strength, search)."""
    d = {}
    for study, spec in STUDIES.items():
        d[study] = {str(s): {q: [r["segment_id"] for r in rank.search(q, k=TOP_K, strength=s)[1]] for q in spec["queries"]}
                    for s in spec["strengths"]}
    (path("reports") / "study_design.json").write_text(json.dumps(d, indent=1), encoding="utf-8")
    return d


def build_queue():
    """Unrated (search, clip) pairs -> docs/study_queue.json for the rating page. Variant is not shown (blind)."""
    d, rated = design(), all_ratings()
    df, _, _ = rank.index()
    start = dict(zip(df.segment_id, df.start_s))
    pairs = sorted({(q, cid) for study in d.values() for per_s in study.values() for q, ids in per_s.items()
                    for cid in ids if f"{q}|{cid}" not in rated})
    rng = random.Random(7)
    by_q = {}
    for q, cid in pairs:
        by_q.setdefault(q, []).append(cid)
    items = []
    for q in sorted(by_q, key=lambda _: rng.random()):  # searches in random order, clips shuffled within each
        ids = by_q[q]
        rng.shuffle(ids)
        items += [{"q": q, "id": cid, "rank": 0, "start_s": float(start[cid])} for cid in ids]
    (ROOT / "docs" / "study_queue.json").write_text(json.dumps({"name": "study", "items": items}, indent=1), encoding="utf-8")
    return len(items)


def category_at(strength):
    """Automatic category check (hybrid, top 10) at a centring strength."""
    df, _, _ = rank.index()
    hits = []
    for q, cat, _ in CATEGORY_QUERIES:
        _, res = rank.search(q, k=10, max_per_show=10, strength=strength)
        hits.append(np.mean([r["category"] == cat for r in res]))
    return float(np.mean(hits))


def results():
    """Score every variant from pooled ratings -> reports/study_results.json."""
    d = json.loads((path("reports") / "study_design.json").read_text(encoding="utf-8"))
    rated = all_ratings()
    out = {}
    for study, per_s in d.items():
        out[study] = []
        for s, qmap in per_s.items():
            vs = [rated.get(f"{q}|{cid}") for q, ids in qmap.items() for cid in ids]
            y, n = sum(v == "y" for v in vs), sum(v == "n" for v in vs)
            per_q = {q: sum(rated.get(f"{q}|{cid}") == "y" for cid in ids) for q, ids in qmap.items()}
            out[study].append({"strength": float(s), "yes": y, "rated": y + n, "missing": sum(v is None for v in vs),
                               "per_query": per_q})
    out["category"] = [{"strength": s, "share": category_at(s)} for s in STUDIES["long"]["strengths"]]
    (path("reports") / "study_results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out
