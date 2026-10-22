# Vibe Search: results

## In 30 seconds

- **What it is:** type how you want a podcast to *sound* ("two friends laughing about football, late-night energy")
  and get back the exact 20-second moments that sound like that, with plain-word reasons
  ("high energy · lots of laughter · topic: football") and a play button.
- **Does it work?** Yes. **A listener judged 33 of the top 48 results (69%) a real match for the vibe**, hearing each
  clip without the show name. Separately, an automatic check finds **71% of the top 10 results come from the right
  kind of show, against 13% at random**, and "find more like this moment" stays with the same show 58% of the time,
  against 2% at random.
- **Best at:** friends' banter, bedtime stories and kids' stories (4 of 4 in the listening test); comedy, sports talk,
  news voices and whispering in the automatic check.
- **Weak at:** heated arguments and "rain and nature sounds" (1 of 4 each; the data has almost no nature-sound shows),
  and "a bedtime story for children" returns adult sleep stories, which sound the same.
- **Finding:** words and sounds sit in separate regions of the embedding space (the modality gap). Correcting for it
  ("centring") finds the right *kind of show* more often, but a listener judged the vibe worse (33 → 27 of 48), so
  search keeps the original embeddings.
- **Cost:** about one cent of LLM spend in total. Everything else runs locally on a laptop.
- **Demo:** `vibe serve` → http://127.0.0.1:8765/

## Corpus

| | |
|---|---|
| Shows | 39 across 10 vibe groups (4 each; kids' stories 3) |
| Audio | 3 recent episodes per show, minutes 2–10 → **2,808 moments**, 15.6 hours |
| Failed feeds | Pardon My Take (timeout), Brains On! (404); Football Daily spare used |
| LLM spend | **$0.0066** (gpt-5-mini via LLM Foundry, 1 cached call per new query; guard at $0.80/day) |
| Compute | ~4 h overnight on a 12-core CPU (audio embedding and Whisper in parallel) |

The README plan was 117 episodes × 15 min with overlap (10,409 moments). This run covers the same 117 episodes,
taking minutes 2–10 with no overlap.

## Phase 1: model choice — EmbeddingGemma 2

15 text prompts against 300 random segments; top 5 checked against the show's vibe group (150 clips to listen to in
`reports/phase1_listen/`).

| | CLAP | EmbeddingGemma 2 |
|---|---|---|
| top 5 from a fitting vibe group | 51% | **70%** (random 13%) |
| prompts won | 3 | **8** |
| CPU time per 20 s moment | 0.37 s | 3.1 s |

EmbeddingGemma 2 also gets news anchors, sports commentary, crime narration and music right, where CLAP fails.
Both are weak on "two people arguing". On CPU it must run in float32; bfloat16 is 12× slower.

## Phase 2: features

Mean percentile per vibe group (0 = lowest in the corpus, 1 = highest):

| vibe | energy | pace | pauses | expressive | laughter | music | crowd |
|---|---|---|---|---|---|---|---|
| asmr/ambient | 0.17 | 0.05 | 0.34 | 0.53 | 0.60 | 0.81 | 0.20 |
| sleep/meditation | 0.39 | 0.30 | 0.73 | 0.30 | 0.38 | 0.62 | 0.31 |
| sports banter | 0.46 | 0.74 | 0.56 | 0.44 | 0.55 | 0.38 | 0.69 |
| interview | 0.51 | 0.58 | 0.51 | 0.52 | 0.55 | 0.35 | 0.60 |
| music-heavy | 0.52 | 0.52 | 0.45 | 0.46 | 0.51 | 0.74 | 0.37 |
| news briefing | 0.53 | 0.52 | 0.46 | 0.54 | 0.30 | 0.43 | 0.58 |
| debate | 0.55 | 0.65 | 0.53 | 0.46 | 0.26 | 0.35 | 0.66 |
| kids stories | 0.56 | 0.42 | 0.57 | 0.68 | 0.58 | 0.60 | 0.40 |
| true crime | 0.59 | 0.56 | 0.48 | 0.51 | 0.51 | 0.47 | 0.42 |
| comedy chat | 0.74 | 0.63 | 0.39 | 0.61 | **0.77** | 0.28 | 0.73 |

Sanity check passes: calm shows are lowest on energy and pace, comedy is highest on laughter and energy, and the
music shows are high on music. The first version of the laughter score failed this check (ASMR and kids' shows
came out above comedy, because "laughing vs talking" also rewards any non-speech sound). The prompts were changed
to contrast speech with speech. That pair was chosen by looking at these group means, so it is light tuning on the
same weak labels.

Simplifications: pitch uses `yin` instead of `pyin` (12 s → under 0.1 s per moment); no voice counting.

## Phase 3: search

Score = 0.4 · sound match + 0.4 · feature fit + 0.2 · topic match, max 2 moments per show. Full results for the
12 demo queries and 3 "more like this" examples: `reports/phase3_search.md`.

| query | top 3 |
|---|---|
| two friends laughing about football, late-night energy | Football Daily, Men in Blazers, Off Menu |
| excited fast talking about sports | Men in Blazers, Bill Simmons ×2 |
| serious news voice reading the headlines | Up First ×2, Criminal |
| soft whispering, very quiet | GentleWhispering ASMR, Nothing Much Happens, GentleWhispering |
| kids story with funny voices | Circle Round ×2, Stories Podcast |
| relaxed chat between comedians, lots of laughs | Armchair Expert, Conan, Off Menu |
| thoughtful slow interview about life | Get Sleepy, Fresh Air, Tara Brach |
| *weak:* heated argument, people talking over each other | Fresh Air ×2, The Journal |
| *weak:* upbeat music and singing | Stories Podcast, Story Seeds, Switched on Pop |

Two general fixes went in after the first results: moments with almost no speech get no topic score (their empty
transcripts all matched "sports"), and the sound match uses the user's own words plus the LLM's description
(long descriptions alone embed poorly).

## Listening test (human judgement)

For each of the 12 demo queries, the top 4 clips were played without the show name (`docs/rate.html`), and one
listener marked each "matches the vibe" or "doesn't". Raw ratings: `reports/listening_test.json`.

| query | matched |
|---|---|
| two friends laughing about football, late-night energy | 4 / 4 |
| calm, slow, one voice, like a bedtime story | 4 / 4 |
| kids story with funny voices | 4 / 4 |
| excited fast talking about sports | 3 / 4 |
| serious news voice reading the headlines | 3 / 4 |
| dramatic storytelling about a murder | 3 / 4 |
| thoughtful slow interview about life | 3 / 4 |
| relaxed chat between comedians, lots of laughs | 3 / 4 |
| soft whispering, very quiet | 2 / 4 |
| upbeat music and singing | 2 / 4 |
| heated argument, people talking over each other | 1 / 4 |
| rain and nature sounds, no talking | 1 / 4 |
| **total** | **33 / 48 (69%)** |

By rank: #1 8/12, #2 9/12, #3 7/12, #4 9/12, so the order within the top 4 barely matters.

This is the direct test: does the clip sound right? The category check below only tests whether results come from the
right *kind of show*. A category describes the show, not the moment, so it can't see laughter in a clip. **Limits:**
one listener (the person who built this), 48 clips, and no randomly picked clips were rated, so there is no human
"chance" baseline to compare 69% against. Next step: several listeners, with random clips mixed in blind.

## Finding: the modality gap, and why search doesn't correct it

In EmbeddingGemma 2's shared space, mean cosine is 0.71 clip↔clip and 0.69 text↔text, but only **0.57 text↔clip**.
In a joint 2-D projection, words form their own island: **0 of 10** of a word's nearest map neighbours are clips.
**Centring** (subtract the catalogue's mean audio vector and the mean of 77 neutral phrases, then re-normalise) moves
words in among the clips (**7 of 10** neighbours are clips). It's two fixed vectors, so it would be cheap in
real-time search. Code: `src/vibe/centering.py`, switch `rank.center`.

**Single words find the right *kind of show* more often after centring** (of the 25 nearest clips: "music" 11 → 19,
"sports" 15 → 21, "laughter" 11 → 17, "news" 15 → 20; "whispering" got worse, 19 → 11). The automatic category check
also rose (sound only 60% → 72%).

**But a second listening round said the vibe got worse: 33 → 27 of 48.** Centring pulled results toward what shows
are *about*. "Upbeat music and singing" returned shows that talk about music (Dissect, Song Exploder): 0/4.
"Excited fast talking about sports" returned calm stretches of sports shows: 0/4. It helped where topic and sound
coincide (news voices 3 → 4, crime storytelling 3 → 4, whispering 2 → 3). Round 2 reused the 21 clip ratings that
were unchanged and rated 27 new clips (14 matched).

**Decision:** live search stays on the original embeddings (`rank.center: false`). Centring is worth having for
topic/category lookups, not for vibe search. The automatic check would have pointed the wrong way; only listening
caught it.

### Study: how much of the gap should search close? (`src/vibe/study.py`)

Partial centring subtracts a share of each mean (0 = raw, 1 = full). Each variant's top 4 clips were rated blind
(the variant was hidden and the order shuffled); 144 (search, clip) ratings were pooled across the rounds. Results are
in `reports/study_results.json`; the design (which clips each variant returned) is in `reports/study_design.json`.

| share of gap closed | 0% | 25% | 50% | 75% | 100% |
|---|---|---|---|---|---|
| 12 long searches (listener, of 48) | **33** | 32 | 32 | **33** | 27 |
| 10 short searches (listener, of 40) | **31** | | 28 | | 26 |
| automatic category check | 71% | 72% | 72% | 72% | 72% |

- **It's a cliff, not a slope:** long searches are flat up to 75%, then drop at full centring.
- **Centring never helps by ear.** Short searches decline steadily.
- **It strips the sound and keeps the topic:** "music" 2 → 1 → 0 (it returns music talk shows), "whispering"
  3 → 2 → 1, "a children's story" 2 → 1 → 1. Topic searches ("sports", "news", "crime", "football", "calm") stay
  at 4/4 at every strength; "laughter" 3/3/3; "rain" 1/1/1 (there's almost no rain in the corpus).
- **The automatic check is flat and blind to this.** The per-word nearest-25 table even rose for "music" (11 → 19),
  because it counts music *talk* shows as hits.
- **Raw embeddings already handle short searches:** 31 of 40.

Rating rules used (the user asked about edge cases mid-test): judge the sound, not the show's category or topic;
"music" needs audible music; whispering needs an actual whisper or a breathy near-whisper (soft, slow voices = No);
the more specific the search, the stricter the match; if the main feeling is missing, No.

## Phase 4: sanity checks (no labelling)

Share of the top 10 from the expected iTunes category:

| half | query | expected | random | sound only | features only | **hybrid** |
|---|---|---|---|---|---|---|
| A | calm guided relaxation | Health & Fitness | 15% | 70% | 60% | **70%** |
| A | comedians joking around | Comedy | 15% | 90% | 50% | **90%** |
| A | crime story narration | True Crime | 10% | 30% | 10% | **70%** |
| A | sports talk | Sports | 10% | 60% | 10% | **100%** |
| B | news headlines briefing | News | 15% | 100% | 50% | **80%** |
| B | a bedtime story for children | Kids & Family | 8% | 0% | 0% | **0%** |
| B | music with singing and instruments | Music | 10% | 40% | 30% | **60%** |
| B | soft whispering to help you sleep | Health & Fitness | 15% | 90% | 0% | **100%** |
| | **mean** | | 13% | 60% | 26% | **71%** |

"More like this" (50 random seeds): **58%** of the top 10 come from the seed's own show, against 2% at random
(sound only 54%, features only 23%).

**What works:** the hybrid beats either signal alone. Sound carries most of it, and the features re-rank (true
crime goes from 30% to 70%, sports from 60% to 100%). **What doesn't:** children's bedtime stories (0%; they sound
like adult sleep stories), arguments, and features on their own.

**Honesty notes:** the weights (0.4/0.4/0.2) were never tuned. The laughter prompts and the two Phase 3 fixes were
decided after looking at results from the smaller first run, so the A/B halves are not a clean held-out test. This
overnight run used the same code with no further changes. Its numbers (71% vs 68% before, 58% vs 43%) come from
more data, not from more tuning.

## Phase 5: demo page

A single file with no build step:
- search box with 12 example chips
- 5 live vibe sliders (energy, pace, laughter, calm/pauses, music)
- results with "why it matched" chips, a play button that streams the publisher's audio at the timestamp, and
  "more like this"
- a UMAP vibe map of all 2,808 moments (colour by show type or any feature; click a dot to play it)

No audio or transcripts are hosted. With `vibe serve` running, a clip that the network blocks plays from the local
cache instead.

## Limits

- Small corpus (117 episodes, 8 minutes each), English only.
- Laughter, music and crowd scores are zero-shot; there is no diarization.
- Episodes with dynamic ad insertion may be slightly off at the timestamp when streamed.
- About half the publishers are blocked on the corporate network, so use `vibe serve` there.
- Internal prototype: flag before any client-facing use with third-party shows.
