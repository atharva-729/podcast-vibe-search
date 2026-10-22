# Vibe Search: results (demo build)

Search podcasts by how they sound. Type a vibe ("two friends laughing about football, late-night energy") and get back
timestamped 20-second moments, each with plain-word reasons ("high energy · lots of laughter · topic: football").

**Demo:** `vibe serve` → http://127.0.0.1:8765/ (live search). `docs/index.html` also works as a static page
with the 12 example queries, the sliders and the map.

## Corpus (demo cut)

| | |
|---|---|
| Shows | 39 across 10 vibe groups (4 each; kids' stories 3) |
| Audio | 1 recent episode per show, minutes 2–8 → **702 moments**, 234 min |
| Failed feeds | Pardon My Take (timeout), Brains On! (404); Football Daily spare used |
| LLM spend | **$0.0066 total** (23 calls, gpt-5-mini via LLM Foundry; budget guard $0.80/day) |

The original plan was 117 episodes × 15 min with overlap (10,409 moments, ~20 h of CPU). It was cut to fit one evening.
Everything else in the plan is built; the full corpus is just a longer run of the same commands.

## Phase 1: model choice — EmbeddingGemma 2

15 text prompts against 300 random segments; top-5 checked against the show's vibe group (listen folder:
`reports/phase1_listen/`, 150 clips).

| | CLAP | EmbeddingGemma 2 |
|---|---|---|
| top-5 from a fitting vibe group | 51% | **70%** (random 13%) |
| prompts won | 3 | **8** |
| CPU time per 20 s moment | 0.37 s | 3.1 s |

EmbeddingGemma 2 also gets news anchors, sports commentary, crime narration and music right, where CLAP fails.
Both are weak on "two people arguing". Note: EmbeddingGemma 2 has to run in float32 on CPU; bfloat16 is 12× slower.

## Phase 2: features

Mean percentile per vibe group (0 = lowest in corpus, 1 = highest):

| vibe | energy | pace | pauses | expressive | laughter | music | crowd |
|---|---|---|---|---|---|---|---|
| asmr/ambient | 0.20 | 0.06 | 0.28 | 0.63 | 0.55 | 0.78 | 0.18 |
| sleep/meditation | 0.37 | 0.32 | 0.71 | 0.28 | 0.32 | 0.58 | 0.32 |
| interview | 0.45 | 0.58 | 0.47 | 0.55 | 0.67 | 0.42 | 0.61 |
| kids stories | 0.50 | 0.47 | 0.72 | 0.69 | 0.57 | 0.58 | 0.42 |
| debate | 0.51 | 0.64 | 0.56 | 0.47 | 0.28 | 0.37 | 0.65 |
| music-heavy | 0.52 | 0.41 | 0.29 | 0.54 | 0.58 | 0.81 | 0.35 |
| news briefing | 0.52 | 0.53 | 0.51 | 0.50 | 0.25 | 0.44 | 0.60 |
| true crime | 0.56 | 0.62 | 0.53 | 0.41 | 0.52 | 0.45 | 0.40 |
| sports banter | 0.65 | 0.74 | 0.54 | 0.45 | 0.54 | 0.35 | 0.74 |
| comedy chat | 0.72 | 0.65 | 0.44 | 0.53 | **0.74** | 0.24 | 0.72 |

Sanity check passes: calm shows are lowest on energy and pace, and comedy is highest on laughter. The first version of
the laughter score failed it: ASMR and kids' shows came out above comedy, because "laughing vs talking" also rewards
any non-speech sound. The prompts were changed to contrast speech with speech. That pair was picked by looking at
these group means, so it is light tuning on the same weak labels.

Compute (12-core CPU, models in parallel): audio embeddings 64 min, Whisper transcripts 59 min, acoustic features 2 min.
Simplifications: pitch via `yin` instead of `pyin` (12 s → <0.1 s per moment); no voice counting.

## Phase 3: search

Score = 0.4 · sound match + 0.4 · feature fit + 0.2 · topic match, max 2 moments per show. Full results for the
12 demo queries and 3 "more like this" examples: `reports/phase3_search.md`. Highlights:

- **"excited fast talking about sports"** → Bill Simmons ×2, WTF (fast pace · high energy)
- **"serious news voice reading the headlines"** → Up First, Criminal, Global News
- **"kids story with funny voices"** → Circle Round, Stories Podcast
- **"thoughtful slow interview about life"** → Tara Brach, Sleep With Me
- **More like Get Sleepy** → Get Sleepy, Nothing Much Happens (flat delivery · slow pace)
- Weak: **"heated argument"** (top hit is Slow Radio) and **"dramatic storytelling about a murder"** (sleep stories
  outrank true crime)

Two fixes went in after seeing the first results. Both are general, not tuned per query:
(1) moments with almost no speech get no topic score (their empty transcripts all matched "sports");
(2) the sound match uses the user's own words plus the LLM's description, because long descriptions alone embed poorly.

## Phase 4: sanity checks (no labelling)

Share of the top 10 from the expected iTunes category:

| half | query | expected | random | sound only | features only | **hybrid** |
|---|---|---|---|---|---|---|
| A | calm guided relaxation | Health & Fitness | 15% | 80% | 80% | **90%** |
| A | comedians joking around | Comedy | 15% | 90% | 70% | **90%** |
| A | crime story narration | True Crime | 10% | 30% | 10% | **50%** |
| A | sports talk | Sports | 10% | 60% | 10% | **80%** |
| B | news headlines briefing | News | 15% | 90% | 30% | **80%** |
| B | a bedtime story for children | Kids & Family | 8% | 20% | 0% | **0%** |
| B | music with singing and instruments | Music | 10% | 20% | 20% | **50%** |
| B | soft whispering to help you sleep | Health & Fitness | 15% | 90% | 20% | **100%** |
| | **mean** | | 12% | 60% | 30% | **68%** |

"More like this" (50 random seeds): **43%** of the top 10 come from the seed's own show, against 2% random
(sound only 41%, features only 19%).

**What works:** calm/sleep, whispering, comedy, sports talk and news are clearly found (80–100% vs ~12% random), and
the hybrid beats either signal alone. **What doesn't:** "bedtime story for children" returns adult sleep stories
(acoustically similar; 0%), "heated argument" is weak, and true crime is only partly found. The feature-only score is
weak by itself; it mostly helps re-rank. Caveat: the weights were never tuned, but the two Phase 3 fixes and the
laughter prompts were decided after looking at results, so the A/B halves are not a clean held-out test.

## Phase 5: demo page

Single file, no build step: search box with 12 example chips, 5 live vibe sliders (energy, pace, laughter,
calm/pauses, music), results with "why it matched" chips, a play button that streams the publisher's audio at the
timestamp, "more like this", and a UMAP vibe map (colour by show type or any feature; click a dot to play).
No audio or transcripts are hosted. With `vibe serve` running, a clip that the network blocks plays from the local
cache instead.

## Limits

Small corpus (39 episodes, 6 minutes each), English only, zero-shot laughter/music/crowd scores, no diarization.
Episodes with dynamic ad insertion may be slightly off at the timestamp when streamed. On the corporate network
about half the publishers are blocked, so use `vibe serve` for playback there. Internal prototype; flag before any
client-facing use with third-party shows.
