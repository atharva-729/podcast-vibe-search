"""Phase 3 demo output + Phase 4 weak-label sanity checks (no labelling).

Weights are fixed from config (0.4/0.4/0.2) and were never tuned, so there is no tuning leak;
queries are still split into A/B halves as the README asks and reported separately.
"""
import json

import numpy as np

from . import llm, rank
from .config import ROOT, path

DEMO_QUERIES = [q.strip() for q in (ROOT / "reports" / "demo_queries.txt").read_text(encoding="utf-8").splitlines()
                if q.strip() and not q.startswith("#")]

CATEGORY_QUERIES = [  # (query, expected iTunes category, half)
    ("calm guided relaxation", "Health & Fitness", "A"),
    ("comedians joking around", "Comedy", "A"),
    ("crime story narration", "True Crime", "A"),
    ("sports talk", "Sports", "A"),
    ("news headlines briefing", "News", "B"),
    ("a bedtime story for children", "Kids & Family", "B"),
    ("music with singing and instruments", "Music", "B"),
    ("soft whispering to help you sleep", "Health & Fitness", "B"),
]
ABLATIONS = {"embedding only": {"vibe": 1, "feature": 0, "topic": 0},
             "features only": {"vibe": 0, "feature": 1, "topic": 0},
             "hybrid": None}
LIKE_ABLATIONS = {"embedding only": (1, 0), "features only": (0, 1), "hybrid": (0.6, 0.4)}


def mmss(s):
    return f"{int(s) // 60}:{int(s) % 60:02d}"


def demo():
    df, _, _ = rank.index()
    L = ["# Phase 3: demo queries (top 5)", ""]
    out = {"queries": {}, "like": {}}
    for q in DEMO_QUERIES:
        p, res = rank.search(q)
        out["queries"][q] = {"parsed": p, "results": res}
        L += [f"## {q}", f"parsed ({p['source']}): vibe_text={p['vibe_text']!r} targets={p['targets']} "
              f"topic={p['topic']!r} avoid={p['avoid']}", "",
              "| # | show | at | score | vibe / feature / topic | why |", "|---|---|---|---|---|---|"]
        for n, r in enumerate(res, 1):
            pp = r["parts"]
            L.append(f"| {n} | {r['show'][:32]} | {mmss(r['start_s'])} | {r['score']} | "
                     f"{pp['vibe']:.2f} / {pp['feature']:.2f} / {pp['topic']:.2f} | {' · '.join(r['why'])} |")
        L.append("")
    seeds = [out["queries"][q]["results"][0]["segment_id"] for q in DEMO_QUERIES[:3]]
    L += ["# More like this", ""]
    for s in seeds:
        seed = df[df.segment_id == s].iloc[0]
        res = rank.like(s, max_per_show=2)
        out["like"][s] = res
        L += [f"## seed: {seed.show} @ {mmss(seed.start_s)}", "", "| # | show | at | score | why |", "|---|---|---|---|---|"]
        L += [f"| {n} | {r['show'][:32]} | {mmss(r['start_s'])} | {r['score']} | {' · '.join(r['why'])} |"
              for n, r in enumerate(res, 1)]
        L.append("")
    L.append(f"LLM spend log: {json.dumps(llm.spend_log())}")
    (path("reports") / "phase3_search.md").write_text("\n".join(L), encoding="utf-8")
    (path("reports") / "phase3_search.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


def category_check():
    df, _, _ = rank.index()
    rows = []
    for q, cat, half in CATEGORY_QUERIES:
        base = float((df.category == cat).mean())
        row = {"query": q, "expected": cat, "half": half, "random": base, "items": {}}
        for name, w in ABLATIONS.items():
            _, res = rank.search(q, k=10, weights=w, max_per_show=10)
            row[name] = float(np.mean([r["category"] == cat for r in res]))
            row["items"][name] = [{"id": r["segment_id"], "show": r["show"], "category": r["category"],
                                   "hit": r["category"] == cat} for r in res]
        rows.append(row)
    return rows


def same_show_check(n_seeds=50, seed=0):
    df, _, _ = rank.index()
    seeds = df.sample(n_seeds, random_state=seed).segment_id.tolist()
    out, items = {}, {}
    for name, (wa, wf) in LIKE_ABLATIONS.items():
        items[name], hits = [], []
        for s in seeds:
            own = df.loc[df.segment_id == s, "show_id"].iloc[0]
            res = rank.like(s, k=10, w_audio=wa, w_feat=wf)
            hits.append(np.mean([r["show_id"] == own for r in res]))
            items[name].append({"seed": s, "hits": [{"id": r["segment_id"], "show": r["show"],
                                                     "hit": r["show_id"] == own} for r in res]})
        out[name] = float(np.mean(hits))
    out["items"] = items
    # random: same-show share among candidates (excluding the seed and its two neighbours)
    sizes = df.groupby("show_id").size()
    out["random"] = float(np.mean([(sizes[df.loc[df.segment_id == s, "show_id"].iloc[0]] - 3) / (len(df) - 3)
                                   for s in seeds]))
    return out


def phase1_summary():
    """Model-pick numbers from the Phase 1 smoke test, for the results page."""
    f = path("reports") / "phase1_smoke.json"
    if not f.exists():
        return None
    s = json.loads(f.read_text(encoding="utf-8"))["summary"]
    return {"random": s["random_baseline_hit_rate"],
            "models": {k: {"hit": s[k]["vibe_hit_rate"], "s_per_segment": s[k]["s_per_segment"],
                           "won": s[k]["prompts_won"]} for k in ("clap", "gemma")}}


def run():
    demo()
    cat = category_check()
    same = same_show_check()
    L = ["# Phase 4: sanity evaluation (weak labels, no labelling)", "",
         "Weights fixed at 0.4/0.4/0.2 from config; nothing was tuned on these queries.", "",
         "## 1+3. Category check: share of top 10 from the expected iTunes category", "",
         "| half | query | expected | random | embedding only | features only | hybrid |", "|---|---|---|---|---|---|---|"]
    for r in cat:
        L.append(f"| {r['half']} | {r['query']} | {r['expected']} | {r['random']:.0%} | {r['embedding only']:.0%} | "
                 f"{r['features only']:.0%} | {r['hybrid']:.0%} |")
    for half in ("A", "B"):
        sub = [r for r in cat if r["half"] == half]
        L.append(f"| {half} | **mean** | | {np.mean([r['random'] for r in sub]):.0%} | "
                 + " | ".join(f"{np.mean([r[k] for r in sub]):.0%}" for k in ABLATIONS) + " |")
    L += ["", "## 2+3. More-like-this: share of top 10 from the seed's own show (50 random seeds, neighbours excluded)", "",
          "| random | embedding only | features only | hybrid |", "|---|---|---|---|",
          f"| {same['random']:.0%} | {same['embedding only']:.0%} | {same['features only']:.0%} | {same['hybrid']:.0%} |"]
    (path("reports") / "phase4_eval.md").write_text("\n".join(L), encoding="utf-8")
    (path("reports") / "phase4_eval.json").write_text(
        json.dumps({"category": cat, "same_show": same, "phase1": phase1_summary(),
                    "spend_usd": sum(d["usd"] for d in llm.spend_log().values())}, indent=1, default=bool),
        encoding="utf-8")
    return cat, same
