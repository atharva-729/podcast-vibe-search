"""vibe <step> — command-line entry point."""
import argparse
import json
import shutil

import pandas as pd

from .config import ROOT, path


def cmd_episodes(args):
    from . import feeds
    df = feeds.run()
    print(f"{len(df)} episodes from {df.show_id.nunique()} shows -> data/episodes.parquet")


def cmd_segments(args):
    from . import audio
    seg = audio.run()
    print(f"{len(seg)} segments -> index/segments.parquet")


def cmd_smoke_llm(args):
    from . import llm
    text, info = llm.chat([{"role": "user", "content": "Reply with exactly: ok"}])
    print(f"reply={text!r} model={info['model']} cached={info['cached']} "
          f"tokens={info['usage']['prompt_tokens']}+{info['usage']['completion_tokens']} cost=${info['usd']:.6f}")
    print(f"spent today: ${llm.spent_today():.6f}")


def cmd_embed_smoke(args):
    from . import phase1
    print(json.dumps(phase1.run(), indent=1))


def cmd_embed(args):
    from . import embed
    shape, secs, new = embed.embed_all(args.model)
    print(f"{args.model}: {shape} -> index/audio_emb.npy, {new} new segments in {secs / 60:.0f} min")


def cmd_transcribe(args):
    from . import transcribe
    t = transcribe.run()
    print(f"{len(t)} segment transcripts, median {t.pace_wpm.median():.0f} wpm -> index/transcripts.parquet")


def cmd_acoustic(args):
    import time
    from . import features
    t = time.time()
    df = features.run_acoustic()
    print(f"{len(df)} segments acoustic features in {time.time() - t:.0f}s -> index/acoustic.parquet")


def cmd_textemb(args):
    from . import textemb
    df = textemb.run()
    print(f"features for {len(df)} segments -> index/features.parquet; transcripts -> index/text_emb.npy")


def _print_results(res):
    for n, r in enumerate(res, 1):
        t = int(r["start_s"])
        print(f"{n}. {r['show'][:40]:40} @{t // 60}:{t % 60:02d}  score={r['score']}  {r['parts']}  "
              f"[{' · '.join(r['why'])}]  id={r['segment_id']}")


def cmd_search(args):
    from . import rank
    p, res = rank.search(args.query, k=args.limit)
    print(f"parsed ({p['source']}): {p}")
    _print_results(res)


def cmd_like(args):
    from . import rank
    _print_results(rank.like(args.segment_id, k=args.limit, max_per_show=2))


def cmd_evaluate(args):
    from . import evaluate
    evaluate.run()
    print((path("reports") / "phase4_eval.md").read_text(encoding="utf-8"))


def cmd_demo(args):
    from . import demo
    print(f"docs/data.js built: {demo.run()}")


def cmd_serve(args):
    from . import server
    server.serve()


def cmd_study_queue(args):
    from . import study
    print(f"{study.build_queue()} clips to rate -> docs/study_queue.json (open /rate.html?queue=study)")


def cmd_study_results(args):
    from . import study
    print(json.dumps({k: v if k == "category" else [{x: r[x] for x in ("strength", "yes", "rated", "missing")} for r in v]
                      for k, v in study.results().items()}, indent=1))


def _dir_mb(p):
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1e6 if p.exists() else 0.0


def cmd_status(args):
    """Checkpoint 0 report."""
    from . import llm
    eps = pd.read_parquet(ROOT / "data" / "episodes.parquet")
    seg = pd.read_parquet(path("index") / "segments.parquet")
    shows = eps.drop_duplicates("show_id")

    print("== Shows per iTunes category ==")
    print(shows.groupby("category").show.apply(lambda s: f"{len(s)}: " + ", ".join(s)).to_string())
    print("\n== Shows per vibe ==")
    print(shows.vibe.value_counts().to_string())

    hours = (seg.groupby("episode_id").end_s.max().sum()) / 3600
    print(f"\n== Corpus ==\n{len(shows)} shows, {len(eps)} episodes, {hours:.1f} h audio, {len(seg)} segments")

    fails = (ROOT / "runs" / "bundle_failures.txt").read_text(encoding="utf-8").strip()
    print(f"\n== Failed feeds ==\n{fails or 'none'}")

    print("\n== Disk ==")
    for name, p in [("models", path("models")), ("raw audio", path("audio_cache")),
                    ("rss", ROOT / "data" / "rss"), ("index", path("index"))]:
        print(f"{name:10} {_dir_mb(p):8.0f} MB")
    print(f"free       {shutil.disk_usage(ROOT).free / 1e9:8.0f} GB")

    print(f"\n== LLM spend ==\n{json.dumps(llm.spend_log(), indent=1)}")


def main():
    ap = argparse.ArgumentParser(prog="vibe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("episodes", cmd_episodes), ("segments", cmd_segments),
                     ("smoke-llm", cmd_smoke_llm), ("status", cmd_status),
                     ("embed-smoke", cmd_embed_smoke), ("embed", cmd_embed), ("transcribe", cmd_transcribe),
                     ("acoustic", cmd_acoustic), ("textemb", cmd_textemb), ("search", cmd_search),
                     ("like", cmd_like), ("evaluate", cmd_evaluate), ("demo", cmd_demo), ("serve", cmd_serve),
                     ("study-queue", cmd_study_queue), ("study-results", cmd_study_results)]:
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        if name == "embed":
            p.add_argument("--model", choices=["gemma", "clap"], required=True)
        if name == "search":
            p.add_argument("query")
        if name == "like":
            p.add_argument("segment_id")
        if name in ("search", "like"):
            p.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
