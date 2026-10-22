"""Phase 1 model pick: 15 text prompts vs ~300 random segments, top-5 per model, saved for listening.

The "vibe hit" column is only a rough proxy (does the hit come from a show whose vibe group
matches the prompt?). The real judgement is listening to reports/phase1_listen/.
"""
import json
import re
import subprocess

import numpy as np
import pandas as pd

from . import embed
from .audio import raw_file
from .config import ROOT, path

PROMPTS = {
    "people laughing": ["comedy chat"],
    "calm soft voice": ["sleep/meditation", "asmr/ambient"],
    "loud crowd": [],
    "music playing": ["music-heavy"],
    "one person speaking slowly": ["sleep/meditation", "asmr/ambient"],
    "two people arguing": ["debate"],
    "whispering": ["asmr/ambient"],
    "rain and nature sounds": ["asmr/ambient"],
    "a storyteller reading a story to children": ["kids stories"],
    "a news anchor reading the headlines": ["news briefing"],
    "excited sports commentary": ["sports banter"],
    "quiet meditation with long pauses": ["sleep/meditation"],
    "dramatic narration of a crime": ["true crime"],
    "friends chatting casually": ["comedy chat", "sports banter", "interview"],
    "guitar and singing": ["music-heavy"],
}
N_SAMPLE, TOP_K, SEED = 300, 5, 0


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def mmss(s):
    return f"{int(s) // 60:02d}:{int(s) % 60:02d}"


def save_clip(ep, start, end, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(start), "-i", str(raw_file(ep.audio_file)),
                        "-t", str(end - start), "-ac", "1", "-b:a", "96k", str(dest)], check=True)


def run():
    seg = pd.read_parquet(path("index") / "segments.parquet")
    eps = pd.read_parquet(ROOT / "data" / "episodes.parquet").set_index("episode_id")
    sample = seg.sample(N_SAMPLE, random_state=SEED).reset_index(drop=True)
    sample = sample.join(eps[["show", "vibe", "audio_file"]], on="episode_id")
    listen = path("reports") / "phase1_listen"

    results, timing = {}, {}
    for name in ("clap", "gemma"):
        print(f"== {name}", flush=True)
        model = embed.load(name)
        cache = path("runs") / "cache" / "phase1" / f"{name}_sample{N_SAMPLE}_seed{SEED}.npy"
        if cache.exists():
            a, spent = np.load(cache), json.loads(cache.with_suffix(".json").read_text())["spent_s"]
        else:
            a, spent = embed.embed_segments(model, sample, log_every=50)
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache, a)
            cache.with_suffix(".json").write_text(json.dumps({"spent_s": spent}))
        audio_h = N_SAMPLE * 20 / 3600
        timing[name] = {"s_per_segment": spent / N_SAMPLE, "compute_min_per_audio_hour": spent / 60 / audio_h}
        q = model.text(list(PROMPTS))
        sims = q @ a.T
        results[name] = {}
        for pi, prompt in enumerate(PROMPTS):
            top = np.argsort(-sims[pi])[:TOP_K]
            rows = []
            for rank, j in enumerate(top, 1):
                r = sample.iloc[j]
                clip = listen / slug(prompt) / f"{name}_{rank}_{r.episode_id.split('_')[0]}_{mmss(r.start_s).replace(':', 'm')}.mp3"
                save_clip(r, r.start_s, r.end_s, clip)
                rows.append({"rank": rank, "show": r.show, "vibe": r.vibe, "at": mmss(r.start_s),
                             "sim": round(float(sims[pi, j]), 3), "hit": r.vibe in PROMPTS[prompt],
                             "clip": str(clip.relative_to(ROOT)).replace("\\", "/")})
            results[name][prompt] = rows
        del model

    base = {p: float(sample.vibe.isin(v).mean()) for p, v in PROMPTS.items() if v}
    summary = {}
    for name, res in results.items():
        scored = [p for p in PROMPTS if PROMPTS[p]]
        summary[name] = {
            "vibe_hit_rate": float(np.mean([np.mean([r["hit"] for r in res[p]]) for p in scored])),
            "prompts_won": 0, **timing[name]}
    for p in base:
        h = {n: np.mean([r["hit"] for r in results[n][p]]) for n in results}
        if h["clap"] != h["gemma"]:
            summary[max(h, key=h.get)]["prompts_won"] += 1
    summary["random_baseline_hit_rate"] = float(np.mean(list(base.values())))

    out = path("reports") / "phase1_smoke.json"
    out.write_text(json.dumps({"summary": summary, "baseline": base, "results": results}, indent=1), encoding="utf-8")
    write_markdown(summary, base, results)
    return summary


def write_markdown(summary, base, results):
    L = ["# Phase 1 smoke test: 15 prompts x 300 random segments", "",
         "`hit` = top result's show is in a vibe group that fits the prompt (rough proxy only; listen to judge).", "",
         "| | CLAP | EmbeddingGemma 2 |", "|---|---|---|",
         f"| vibe hit rate (top-5, 14 scored prompts) | {summary['clap']['vibe_hit_rate']:.0%} | {summary['gemma']['vibe_hit_rate']:.0%} |",
         f"| random baseline | {summary['random_baseline_hit_rate']:.0%} | {summary['random_baseline_hit_rate']:.0%} |",
         f"| prompts won (higher hit rate) | {summary['clap']['prompts_won']} | {summary['gemma']['prompts_won']} |",
         f"| embed time per segment (CPU) | {summary['clap']['s_per_segment']:.2f} s | {summary['gemma']['s_per_segment']:.2f} s |",
         f"| compute per hour of segment audio | {summary['clap']['compute_min_per_audio_hour']:.0f} min | {summary['gemma']['compute_min_per_audio_hour']:.0f} min |",
         ""]
    for prompt in results["clap"]:
        L += [f"## {prompt}", f"expected vibes: {', '.join(PROMPTS[prompt]) or '(not scored)'}"
              + (f" · random baseline {base[prompt]:.0%}" if prompt in base else ""), "",
              "| # | CLAP | EmbeddingGemma 2 |", "|---|---|---|"]
        for c, g in zip(results["clap"][prompt], results["gemma"][prompt]):
            cell = lambda r: f"{'✅' if r['hit'] else '·'} {r['show'][:30]} @{r['at']} ({r['sim']})"
            L.append(f"| {c['rank']} | {cell(c)} | {cell(g)} |")
        L.append("")
    (path("reports") / "phase1_smoke.md").write_text("\n".join(L), encoding="utf-8")
