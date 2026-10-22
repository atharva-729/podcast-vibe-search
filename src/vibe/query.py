"""Query -> {vibe_text, targets, topic, avoid}. One cached LLM call; keyword fallback if it fails."""
import json
import re

from . import cache, llm
from .features import FEATURES

LEVELS = {"low", "mid", "high"}
SYSTEM = f"""You turn a podcast "vibe search" query into JSON for a ranking engine.
Return ONLY a JSON object with keys:
- "vibe_text": short description of how the audio should SOUND (voices, mood, sounds), no topic words.
- "targets": object mapping any of {FEATURES} to "low" | "mid" | "high". Include only features the query implies.
  energy = loudness/intensity; expressiveness = pitch variation (animated vs monotone); pace_wpm = speaking speed;
  pause_ratio = share of silence; music_score / laughter_score / crowd_score = presence of music / laughter / crowd noise.
- "topic": the subject being talked about (e.g. "football"), or null if none.
- "avoid": list like ["music_score:high"] for things the query excludes; [] if none."""

KEYWORDS = {  # fallback: word -> targets
    "calm": {"energy": "low", "pace_wpm": "low"}, "relax": {"energy": "low", "pace_wpm": "low"},
    "sleep": {"energy": "low", "pace_wpm": "low", "pause_ratio": "high"}, "slow": {"pace_wpm": "low"},
    "bedtime": {"energy": "low", "pace_wpm": "low"}, "quiet": {"energy": "low"}, "soft": {"energy": "low"},
    "whisper": {"energy": "low"}, "meditat": {"energy": "low", "pause_ratio": "high"},
    "fast": {"pace_wpm": "high"}, "energ": {"energy": "high"}, "loud": {"energy": "high"},
    "excit": {"energy": "high", "expressiveness": "high"}, "heated": {"energy": "high", "pace_wpm": "high"},
    "argu": {"energy": "high", "pace_wpm": "high"}, "laugh": {"laughter_score": "high"},
    "funny": {"laughter_score": "high"}, "joke": {"laughter_score": "high"}, "music": {"music_score": "high"},
    "song": {"music_score": "high"}, "crowd": {"crowd_score": "high"}, "monoton": {"expressiveness": "low"},
}


def validate(d):
    if not isinstance(d, dict) or not isinstance(d.get("vibe_text"), str) or not d["vibe_text"].strip():
        raise ValueError("vibe_text missing")
    targets, avoid = d.get("targets") or {}, d.get("avoid") or []
    if not isinstance(targets, dict) or not isinstance(avoid, list):
        raise ValueError("targets must be an object, avoid a list")
    # Keep the valid parts; drop invented features or levels rather than discarding the whole parse.
    targets = {k: v for k, v in targets.items() if k in FEATURES and v in LEVELS}
    avoid = [a for a in map(str, avoid) if a.partition(":")[0] in FEATURES and a.partition(":")[2] in LEVELS]
    topic = d.get("topic")
    return {"vibe_text": d["vibe_text"].strip(), "targets": targets,
            "topic": topic.strip() if isinstance(topic, str) and topic.strip() else None, "avoid": avoid}


def fallback(q):
    targets = {}
    for word, t in KEYWORDS.items():
        if word in q:
            targets.update(t)
    return {"vibe_text": q, "targets": targets, "topic": None, "avoid": [], "source": "keywords"}


def normalise(q):
    return re.sub(r"\s+", " ", q.strip().lower())


def parse(q):
    q = normalise(q)
    hit = cache.get("query", q)
    if hit:
        return hit
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}]
    for attempt in range(2):  # retry once on bad JSON
        try:
            text, _ = llm.chat(messages if attempt == 0 else messages + [
                {"role": "user", "content": "That was not valid. Return only the JSON object."}])
            m = re.search(r"\{.*\}", text, re.S)
            return cache.put("query", q, {**validate(json.loads(m.group(0))), "source": "llm"})
        except llm.BudgetExceeded:
            break
        except Exception:
            continue
    return fallback(q)  # not cached, so the LLM is tried again next time
