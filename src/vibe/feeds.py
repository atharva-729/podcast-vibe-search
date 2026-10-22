"""Feed metadata (from the imported bundle) -> data/episodes.parquet."""
import json
from collections import defaultdict

import pandas as pd

from .config import ROOT, cfg

SHOWS_PER_VIBE = 4


def load_bundle():
    return json.loads((ROOT / "data" / "bundle_episodes.json").read_text(encoding="utf-8"))


def pick_shows(feeds):
    """Main shows with a full set of episodes; spares fill a vibe only when a main show is missing."""
    n = cfg()["audio"]["episodes_per_show"]
    usable = [f for f in feeds if sum(1 for e in f["episodes"] if e.get("file")) >= n]
    by_vibe = defaultdict(list)
    for f in sorted(usable, key=lambda f: f["spare"]):  # mains first
        if len(by_vibe[f["vibe"]]) < SHOWS_PER_VIBE:
            by_vibe[f["vibe"]].append(f)
    return [f for shows in by_vibe.values() for f in shows]


def build_episodes(feeds):
    rows = []
    for f in pick_shows(feeds):
        top = next((c for c in f["itunes_categories"] if ">" not in c), None)
        sub = next((c.split(" > ")[1] for c in f["itunes_categories"] if ">" in c), None)
        for e in f["episodes"]:
            if not e.get("file"):
                continue
            rows.append({
                "episode_id": e["id"], "show_id": f["show_id"], "show": f["show"], "vibe": f["vibe"],
                "category": top, "subcategory": sub, "spare": f["spare"], "show_link": f["link"],
                "title": e["title"], "pub": e["pub"], "duration_s": e["duration_s"],
                "audio_url": e["audio_url"], "audio_file": e["file"],
            })
    return pd.DataFrame(rows)


def run():
    df = build_episodes(load_bundle())
    out = ROOT / "data" / "episodes.parquet"
    df.to_parquet(out, index=False)
    return df
