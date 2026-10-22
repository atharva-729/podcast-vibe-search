"""Phase 5: precompute everything the static page needs -> docs/data.js (no transcripts, no audio)."""
import json

import numpy as np
import pandas as pd

from . import rank
from .config import ROOT, cfg, path
from .evaluate import DEMO_QUERIES
from .features import FEATURES

# Words shown as buttons on the map. "a crowd cheering" and "music playing" are left out: this corpus has little
# of either, and their nearest clips are mostly ASMR (see reports/REPORT.md).
MAP_WORDS = ["people laughing", "a calm soothing voice", "whispering", "a news anchor", "excited sports talk",
             "a tense crime story", "a storyteller reading to children", "rain and nature sounds"]


GAP_WORDS = ["laughter", "music", "news", "sports", "a calm voice", "a crime story", "rain", "a children's story",
             "whispering", "football"]
# The show type each word should find, for the before/after table.
GAP_EXPECT = {"laughter": "comedy chat", "music": "music-heavy", "news": "news briefing", "sports": "sports banter",
              "a calm voice": "sleep/meditation", "a crime story": "true crime", "rain": "asmr/ambient",
              "a children's story": "kids stories", "whispering": "asmr/ambient", "football": "sports banter"}


def modality_gap_plots(audio, vibes):
    """Clips + words projected together, before and after centring (UMAP, same settings both times)."""
    import umap
    from sklearn.neighbors import NearestNeighbors

    from . import centering
    enc = rank.encoder()
    gen, lab = enc.text(centering.GENERIC_PHRASES), enc.text(GAP_WORDS)
    n, g = len(audio), len(centering.GENERIC_PHRASES)
    out = {}
    for name, a, t in [("raw", audio, np.vstack([gen, lab])),
                       ("centred", centering.audio(audio), centering.text(np.vstack([gen, lab])))]:
        xy = umap.UMAP(n_neighbors=15, min_dist=0.15, metric="cosine", random_state=0).fit_transform(np.vstack([a, t]))
        # Full min-max (no outlier clipping): the word island in the raw plot is the point, so keep it visible.
        xy = ((xy - xy.min(0)) / (xy.max(0) - xy.min(0))).round(4)
        # How many of each word's 10 nearest neighbours on this map are clips (rather than other words)?
        nn = NearestNeighbors(n_neighbors=11).fit(xy)
        near_clips = [float(np.mean([j < n for j in nn.kneighbors(xy[n + g + k:n + g + k + 1])[1][0][1:]]))
                      for k in range(len(GAP_WORDS))]
        out[name] = {"clips": xy[:n].tolist(), "phrases": xy[n:n + g].tolist(),
                     "words": [{"w": w, "x": float(xy[n + g + k, 0]), "y": float(xy[n + g + k, 1])} for k, w in enumerate(GAP_WORDS)],
                     "near_clips": round(float(np.mean(near_clips)), 3)}
    # Per word: how many of its 25 nearest clips are the expected show type, before and after centring.
    ac = centering.audio(audio)
    out["lift"] = []
    for w, q in zip(GAP_WORDS, lab):
        top_raw = np.argsort(-(audio @ q))[:25]
        top_c = np.argsort(-(ac @ centering.text(q[None])[0]))[:25]
        out["lift"].append({"w": w, "expect": GAP_EXPECT[w], "raw": int(np.sum(vibes[top_raw] == GAP_EXPECT[w])),
                            "centred": int(np.sum(vibes[top_c] == GAP_EXPECT[w]))})
    # Cosine statistics behind the gap (raw space).
    rng = np.random.default_rng(0)
    i, j = rng.integers(0, n, 3000), rng.integers(0, n, 3000)
    tt = gen @ gen.T
    out["cos"] = {"audio_audio": round(float(np.mean(np.sum(audio[i] * audio[j], 1))), 3),
                  "text_text": round(float(tt[np.triu_indices(g, 1)].mean()), 3),
                  "text_audio": round(float((gen @ audio.T).mean()), 3)}
    return out


def study_data():
    """Centring-strength study (src/vibe/study.py): scores per strength, plus each clip's rating for the pip grids."""
    from . import study
    res_f, des_f = path("reports") / "study_results.json", path("reports") / "study_design.json"
    if not (res_f.exists() and des_f.exists()):
        return None
    res, des, rated = json.loads(res_f.read_text(encoding="utf-8")), json.loads(des_f.read_text(encoding="utf-8")), study.all_ratings()
    pips = {name: {s: {q: [{"id": cid, "v": rated.get(f"{q}|{cid}")} for cid in ids] for q, ids in qmap.items()}
                   for s, qmap in per_s.items()} for name, per_s in des.items()}
    return {"long": [{k: r[k] for k in ("strength", "yes", "rated")} for r in res["long"]],
            "short": [{k: r[k] for k in ("strength", "yes", "rated")} for r in res["short"]],
            "category": res["category"], "pips": pips}


def run():
    df, audio, _ = rank.index()
    import umap
    xy = umap.UMAP(n_neighbors=15, min_dist=0.15, metric="cosine", random_state=0).fit_transform(audio)
    # Scale to the 1st-99th percentile so a few outliers don't squash the map; outliers sit on the edge.
    lo, hi = np.percentile(xy, 1, axis=0), np.percentile(xy, 99, axis=0)
    xy = ((xy - lo) / (hi - lo)).clip(0, 1)

    shows = df.drop_duplicates("show_id")[["show_id", "show", "title", "category", "vibe", "audio_url"]]
    show_idx = {s: i for i, s in enumerate(shows.show_id)}
    eps = pd.read_parquet(ROOT / "data" / "episodes.parquet").set_index("episode_id")
    links = df.drop_duplicates("show_id").episode_id.map(eps.show_link).tolist()

    pct = df[[f + "_pct" for f in FEATURES]].to_numpy().round(3)
    segs = [{"id": sid, "s": show_idx[sh], "t": float(t), "f": pct[i].tolist(),
             "x": round(float(xy[i, 0]), 4), "y": round(float(xy[i, 1]), 4)}
            for i, (sid, sh, t) in enumerate(zip(df.segment_id, df.show_id, df.start_s))]

    queries = {}
    for q in DEMO_QUERIES:
        p, score, vibe_n, fit, topic_n = rank.score_all(q)
        _, top = rank.search(q, k=10)
        queries[q] = {"parsed": {k: p[k] for k in ("vibe_text", "targets", "topic", "avoid")},
                      "score": [round(float(v), 3) for v in score],
                      "top": [{"id": r["segment_id"], "parts": r["parts"], "why": r["why"]} for r in top]}

    like = {r.segment_id: [x["segment_id"] for x in rank.like(r.segment_id, k=5, max_per_show=2)]
            for r in df.itertuples()}

    ev = json.loads((path("reports") / "phase4_eval.json").read_text(encoding="utf-8"))
    # Sound fingerprint per vibe group: mean corpus percentile of each feature.
    prof = df.groupby("vibe")[[f + "_pct" for f in FEATURES]].mean().round(2)
    profile = {v: prof.loc[v].tolist() for v in prof.index}
    # Words on the map: the clips whose audio embedding is closest to each word's text embedding.
    words = [{"w": w, "ids": rank.nearest_clips(w)} for w in MAP_WORDS]
    # Human listening tests (docs/rate.html): v1 = raw embeddings (the live search), centred = round 2.
    def load_lt(name):
        f = path("reports") / name
        if not f.exists():
            return None, {}
        lt = json.loads(f.read_text(encoding="utf-8"))
        return [{"q": it["q"], "id": it["id"], "rank": it["rank"], "v": lt["ratings"].get(f"{it['q']}|{it['id']}")}
                for it in lt["items"]], lt["ratings"]
    listening_v1, ratings_v1 = load_lt("listening_test_v1.json")
    listening_centred, _ = load_lt("listening_test_centred.json")
    # The listening round that matches the live search setting.
    listening = listening_centred if cfg()["rank"].get("center") else listening_v1
    gap = modality_gap_plots(audio, df.vibe.to_numpy())
    study = study_data()
    data = {
        "features": FEATURES,
        "shows": [{"name": s.show, "episode": s.title, "category": s.category, "vibe": s.vibe,
                   "url": s.audio_url, "link": links[i]} for i, s in enumerate(shows.itertuples())],
        "segments": segs, "queries": queries, "like": like, "eval": ev, "profile": profile, "listening": listening, "listening_v1": listening_v1, "listening_centred": listening_centred,
        "ratings_v1": ratings_v1,
        "words": words, "gap": gap, "study": study,
        "stats": {"shows": len(shows), "segments": len(df), "episodes": int(df.episode_id.nunique()),
                  "minutes": round(float((df.end_s - df.start_s).sum() / 60))},
    }
    (ROOT / "docs" / "data.js").write_text("window.VIBE = " + json.dumps(data, separators=(",", ":")) + ";",
                                           encoding="utf-8")
    return data["stats"]
