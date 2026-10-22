# Vibe Search

Search podcasts by **how they sound**, not just by what they're about.

> "two friends laughing about football, late-night energy"
> "calm, slow, one voice, like a bedtime story"
> "heated argument, people talking over each other"
> "more like *this* 30 seconds"

Normal podcast search matches titles, descriptions and transcripts (the *topic*). Vibe Search also matches the *feel*: energy, pace, laughter, calm, music, how many voices, and how chaotic it is. You get back **moments** (timestamped segments), not just shows, and can play them right where the vibe happens.

Context: an innovation-team build with a Spotify hook. It's also the product version of `gemma-study`: a shared audio–text embedding space used for something real.

> **Status:** this README is the original build plan. For what was actually built, what changed and why, and the
> current results, see **[PROJECT_STATUS.md](PROJECT_STATUS.md)**.

## Running the demo

**Results:** [reports/REPORT.md](reports/REPORT.md)

```
.venv\Scripts\vibe.exe serve          # http://127.0.0.1:8765/  (live search + local audio fallback)
.venv\Scripts\vibe.exe search "calm, slow, one voice"
```

`docs/index.html` also opens on its own as a static page (example queries, sliders, map).
To rebuild from the imported bundle: `vibe episodes → segments → embed --model gemma → transcribe → acoustic → textemb → evaluate → demo`.

---

## How it works (one-paragraph version)

Every episode is cut into short segments (~20 s). For each segment we store three kinds of signal:

1. **An audio embedding** from a model that puts audio and text in the same space, so a text query can be compared directly with sound.
2. **Measurable sound features**, computed with plain code: loudness and energy, pitch variation (expressive vs monotone), speaking rate, pauses, music present, and laughter.
3. **What's being talked about**: a fast local transcript, turned into a text embedding.

A query is turned into the same three things: an embedding of the query text, target values for the features (e.g. "calm" means low energy, slow pace, few pauses), and a topic. Results are ranked by a weighted mix of the three, and each result says **why** it matched ("lots of laughter · 2+ voices · fast pace · topic: football").

## How much AI / LLM

| Part | What does it | Cost |
|---|---|---|
| Audio + text embeddings | Local open model | Free |
| Transcripts | Local Whisper (`faster-whisper`, small model) | Free |
| Sound features | `librosa` / numpy, plus zero-shot laughter and music scores from the embedding model | Free |
| Query → target feature values | **1 cheap LLM call per new query** (cached) | ~$0.0005 per query |
| Episode "vibe card" text (optional) | Template from features first; cheap LLM only if templates read badly | Cents, total |

Everything heavy runs locally. The LLM (through LLM Foundry, budget $1 a day) only interprets queries. **Hard budget guard:** the client tracks spend and refuses calls past $0.80 a day.

---

## How to use this README (for Claude Code)

- Work **one phase at a time**. At each **CHECKPOINT**, stop, show what it asks for, and wait for a go-ahead.
- Don't build later phases early. Don't add dependencies that aren't listed here without asking.
- Keep it simple: Python, files on disk (Parquet + NumPy arrays), a small CLI. No vector DB (brute-force cosine is fine at this size), no agent framework, no web framework beyond a tiny local server in Phase 5.
- If a sanity check fails, stop and report. Don't hide it.

## Ground rules

**Do**
- Cache everything: downloads, embeddings, transcripts, LLM calls. Rerunning must be close to free.
- Keep model names in `config.yaml`. LLM calls go through LLM Foundry (`LLMFOUNDRY_TOKEN` env var) on the cheapest available model.
- Log spend per day to `runs/spend.json`, and stop LLM calls at $0.80 a day.
- Store only **derived data** (embeddings, features, transcripts) plus the episode's original audio URL.
- Write tests for the deterministic parts: segmenting, features, ranking maths.

**Don't**
- Don't re-host or publish any podcast audio, and don't put transcripts on the public page. The demo plays audio from the publisher's own URL at the right timestamp.
- Don't use Spotify's API (most audio-feature endpoints are closed to new apps). We compute our own features.
- Don't do any manual labelling. Evaluation uses signals that already exist (see Phase 4).
- Don't use paid APIs other than the LLM Foundry query parser.

---

## Data

- **Source:** public podcast RSS feeds. Each feed gives the episode audio URL, show title, description and **iTunes category** (Comedy, True Crime, Health & Fitness → Meditation, Sports, News…). That category is our free weak label for evaluation.
- **Size (v1):** about 40 shows × 3 episodes, **first 15 minutes** of each, which is about 30 hours of audio and about 5,400 segments of 20 s each. This keeps local compute manageable.
- **Pick shows for vibe spread**, not popularity: comedy chat, sleep/meditation, true crime, sports banter, news briefing, interview, ASMR/ambient, debate, kids' stories, music-heavy shows.
- `data/feeds.yaml`: list of feed URLs. `data/episodes.parquet`: one row per episode (show, title, category, audio URL, duration, publish date).
- **Rights:** this is an internal prototype. Audio is processed locally and discarded after feature extraction (`--keep-audio` is off by default). Flag to Anand before any client-facing use with third-party shows.

## Repo layout

```
vibe-search/
  README.md  config.yaml
  data/feeds.yaml  data/episodes.parquet  data/audio_cache/ (gitignored)
  index/segments.parquet  index/audio_emb.npy  index/text_emb.npy  index/features.parquet
  src/vibe/
    feeds.py      # RSS → episodes
    audio.py      # download, trim, resample, segment
    embed.py      # audio + text embeddings (shared space)
    features.py   # loudness, pitch var, pace, pauses, music, laughter
    transcribe.py # faster-whisper
    query.py      # LLM query parser → target features (+ cache, budget guard)
    rank.py       # hybrid scoring + explanations
    evaluate.py   # weak-label sanity checks
    server.py     # tiny local search API (Phase 5)
    cli.py
  docs/           # GitHub Pages demo
  runs/  reports/  tests/
```

CLI shape: `vibe <step> [--show X] [--limit N]`, `vibe search "query"`, `vibe like <segment_id>`

---

## Phase 0: Setup and corpus

1. Scaffold the repo, config, caching helpers, the LLM Foundry client with spend guard, and a smoke-test call.
2. Write `data/feeds.yaml` with about 40 public feeds across the vibe spread above. Parse them into `episodes.parquet`, picking the 3 most recent full episodes per show (skip trailers and bonus clips under 10 minutes).
3. Download, trim to the first 15 minutes, resample to mono 16 kHz (or whatever the embedding model needs), and cut into **20 s segments with 10 s overlap**. Store segment metadata (episode, start, end) in `segments.parquet`.

**Don't:** run any model yet.

### CHECKPOINT 0
Show:
- Shows per category.
- Total hours and segment count.
- Any feeds that failed and why.
- Disk usage.
- One LLM Foundry smoke call with its logged cost.

---

## Phase 1: Shared audio–text embeddings

**Goal:** every segment gets an embedding that a **text** query can be compared against.

**Model choice:** a quick pick, not a study.
- Candidate A: **EmbeddingGemma 2**, the multimodal version from `gemma-study`. Verify on its model card that it really accepts audio and puts it in the same space as text; check licence and input length.
- Candidate B: **LAION-CLAP** (`laion/clap-htsat-unfused` or the music variant). A proven audio–text model, run locally.
- Smoke test: 15 fixed text prompts ("people laughing", "calm soft voice", "loud crowd", "music playing", "one person speaking slowly", "two people arguing"…). For each, show the top 5 segments from about 300 random segments, with audio snippets saved locally in `reports/phase1_listen/` so Atharva can listen quickly.
- Pick whichever ranks sensibly more often. If both are weak on speech vibes, still go on: Phase 2's features carry the vibe signal, and the embedding then mainly does sound-event matching.

Then embed all segments and save to `index/audio_emb.npy`, L2-normalised.

**Don't:** fine-tune anything, or spend more than half a day on the model choice.

### CHECKPOINT 1
Show:
- Which model was picked and why (2–3 lines).
- The 15-prompt top-5 table, plus the listen folder.
- Embedding time per hour of audio.

---

## Phase 2: Sound features and transcripts

**Goal:** interpretable numbers per segment, so results can be explained and filtered.

Per segment (`features.parquet`):

| Feature | How |
|---|---|
| `energy` | RMS loudness, mean and variance (librosa) |
| `expressiveness` | Pitch (f0) variance over voiced frames (librosa pyin; subsample to keep it fast) |
| `pace_wpm` | Words per minute from Whisper word timestamps |
| `pause_ratio` | Share of the segment that is silence (energy threshold) |
| `music_score` | Zero-shot: similarity to "music playing" vs "people talking" in the shared space |
| `laughter_score` | Zero-shot: similarity to "people laughing" vs "people talking" |
| `crowd_score` | Zero-shot: crowd / audience noise |
| `voices_est` (optional) | Rough count of distinct voices by clustering short speaker embeddings (e.g. `resemblyzer`). Skip it if it's slow or unreliable, and say so |

- Transcripts: `faster-whisper` small model, int8 on CPU, with word timestamps. Store per segment.
- Text embedding of each segment's transcript, in the same model family as the query encoder, saved to `index/text_emb.npy`. Used only for the topic part of the score.
- Normalise every feature to a 0–1 percentile **within the corpus**, so "high energy" means high compared with other podcasts.

**Don't:** run full speaker diarization (pyannote etc.). It's too heavy for v1.

### CHECKPOINT 2
Show:
- Feature distributions by show category. Sanity check: meditation shows should come out lowest on energy and pace, and comedy highest on laughter. If not, stop.
- Compute time for transcripts and features.
- 5 example segments with all their features.

---

## Phase 3: Search engine

**Query parsing** (`query.py`): one LLM call turns the query into JSON:

```json
{"vibe_text": "two friends laughing, relaxed banter",
 "targets": {"energy": "mid", "laughter_score": "high", "pace_wpm": "fast", "voices_est": "2+"},
 "topic": "football",
 "avoid": ["music_score:high"]}
```

- Allowed target values: `low | mid | high`, or omitted. Validate with a schema and retry once on bad JSON.
- If the LLM fails or the budget is used up, fall back to a keyword map ("calm" → low energy and pace, and so on). Search must never break because of the budget.
- Cache the result per normalised query string.

**Ranking** (`rank.py`):
- `vibe_sim` = cosine(query embedding of `vibe_text`, segment audio embedding).
- `feature_fit` = how close the segment's percentiles are to the targets (low ≈ 0.2, mid ≈ 0.5, high ≈ 0.8), averaged over the targets given.
- `topic_sim` = cosine(topic text embedding, segment transcript embedding). Zero weight if there's no topic.
- `score = w_v·vibe_sim + w_f·feature_fit + w_t·topic_sim`. Weights live in config, starting at 0.4 / 0.4 / 0.2.
- Merge overlapping hits from the same episode, return the top segments, and allow at most 2 per show so one show doesn't flood the results.
- **Explanation** per result: the top 2–3 features that matched, plus the topic match, all as plain words generated from the numbers (no LLM).

**More like this:** pick a segment, then rank by its audio embedding plus feature closeness. No LLM.

**Don't:** use an LLM to rerank results.

### CHECKPOINT 3
Show `vibe search` output for 12 fixed demo queries (saved in `reports/demo_queries.txt`): top 5 each with show, timestamp, score parts and explanation. Include 3 "more like this" examples. Report LLM spend so far.

---

## Phase 4: Sanity evaluation (no labelling)

Quick checks to show it isn't random. **Not** a benchmark.

1. **Category check:** 8 queries that map clearly to an iTunes category ("calm guided relaxation" → meditation, "comedians joking around" → comedy, "crime story narration" → true crime, "sports talk" → sports). Report the share of the top 10 that come from the expected category, against a random baseline.
2. **Same-episode check:** for "more like this", how often the top 10 include other segments from the same episode or show (a vibe should be fairly consistent within a show), against random.
3. **Ablation:** run checks 1 and 2 with embedding only, features only, and the full hybrid.

**Don't:** tune weights on these same queries and then report on them. Hold out half the queries.

### CHECKPOINT 4
Show the three tables, then say in one paragraph what works and what doesn't (e.g. "laughter and calm work; 'heated argument' is weak").

---

## Phase 5: Demo

Two modes:

- **Live (local):** `vibe serve` runs a tiny local API (standard-library `http.server` or a single-file FastAPI app) that the page calls for arbitrary queries.
- **Static (GitHub Pages):** the page ships the 12 demo queries' results and the feature table precomputed, so it works with no server. Live mode is optional when running locally.

Page (`docs/index.html`, single file, no build step):
1. A **search box** with example query chips, plus **vibe sliders** (energy, pace, laughter, calm/pauses, music) that re-filter results live from the precomputed features.
2. A **results list**: show, episode, timestamp, the "why it matched" chips, and a **play** button that streams the publisher's audio URL from that timestamp (`<audio>` + `currentTime`). If a feed blocks this, link out instead.
3. A **vibe map**: a 2-D UMAP of all segments, coloured by category or any feature. Click a dot to play that moment. Hovering a result highlights it on the map.
4. A **"how it works"** section and **limits** (small corpus, English only, first 15 minutes per episode, zero-shot laughter and music scores, no diarization), plus the Phase 4 numbers.
5. Footer: shows are credited by name and link, audio is streamed from the publishers, and it's an internal prototype.

**Don't:** embed or host audio files, put full transcripts on the page, or add a framework or build tooling.

### CHECKPOINT 5
Page works offline in static mode, the sliders filter, play-at-timestamp works for at least 90% of results, live mode works locally, and every number on the page comes from `reports/`.

---

## Phase 6 (optional): Extras

Pick at most one:
- **Vibe drift:** given a start moment and an end vibe, build a 5-step listening path that moves gradually between them (shortest path through a nearest-neighbour graph of segments). This is the "song bridge" idea, for podcasts.
- **Music mode:** add a Creative Commons music corpus (Free Music Archive, `fma_small`). Same pipeline, with features swapped for tempo and key.
- **Show vibe cards:** one-glance profiles per show ("high laughter, fast, 2–3 voices, little music"), made from templates.

---

## Rough timeline

| Phase | Time |
|---|---|
| 0 Corpus | ½–1 day |
| 1 Embeddings | 1 day |
| 2 Features + transcripts | 1–1½ days (mostly compute) |
| 3 Search engine | 1 day |
| 4 Sanity eval | ½ day |
| 5 Demo | 1½–2 days |
| 6 Extra (optional) | 1 day |

About **6–7 working days** to the demo. LLM spend should stay well under $1 total.

## Out of scope (v1)
- Full episodes and large catalogues (no vector DB or ANN).
- Speaker diarization, emotion recognition models, or fine-tuning.
- Non-English shows.
- User accounts, uploads, or a hosted service.

