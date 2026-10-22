# Vibe Search: findings and technical context (for follow-up projects)

**Purpose of this file:** a self-contained briefing for an AI assistant (or engineer) starting a project that builds on
this one. It records **what was built, exactly how, what was measured, what was learned about audio–text embeddings,
what failed, and what's still open**, with the numbers. Companion files: `PROJECT_STATUS.md` (project history and
state), `reports/REPORT.md` (results tables), `docs/explain.html` (an intuitive explainer), `TALKING_POINTS.md`
(the presentation). Repo: https://github.com/atharva-729/podcast-vibe-search. Last updated 2026-10-22.

---

## 0. Summary in 10 lines

1. **Goal:** search podcasts by *how they sound* ("two friends laughing about football, late-night energy") and
   return timestamped 20-second clips. Spotify has no such feature.
2. **Core bet:** a multimodal embedding model (**Google EmbeddingGemma 2**) puts audio and text in **one 768-d space**,
   so text queries can be compared with audio by cosine, with **no labels, classifiers or training**.
3. **Corpus:** 39 public podcasts × 3 episodes × minutes 2–10 → **2,808 clips** of 20 s (15.6 h), embedded on a
   laptop CPU.
4. **Headline result (human, blind):** **33 of 48** top-4 results sounded right for 12 long vibe searches; **31 of 40**
   for 10 one- or two-word searches.
5. **The model is strong on *how people talk*** (speaking style, mood: 27/32) and **weak on specific non-speech sounds**
   (music, rain, whispering: 5/12) and **interaction emotion** (hostility in arguments: 1/4).
6. **Modality gap measured:** mean cosine clip↔clip 0.705, word↔word 0.687, **word↔clip 0.575**. In a joint UMAP,
   **0/10** of a word's nearest neighbours are clips.
7. **Centring** (subtract each modality's mean vector) **closes the gap geometrically** (7/10 neighbours become clips)
   and improves *category* retrieval, **but makes vibe search worse by ear**: 33 → 27 (long), 31 → 26 (short).
   Partial centring (25–75%) gives no gain. It's a cliff at 100%.
8. **Interpretation (hypothesis):** the mean/shared direction carries part of the **acoustic character**; removing it
   shifts matching from *sound* to *topic* ("music" → shows that *talk about* music).
9. **Methodological lesson:** the cheap automatic metric (iTunes-category match) stayed flat or **rose** while human
   judgement fell. **Proxy metrics can point the wrong way for vibe; listening is required.**
10. **Live search uses raw (uncentred) embeddings.** Total LLM spend for the whole project: **$0.0066**.

---

## 1. The project

- **Framing:** an innovation-team prototype with a "Spotify hook", presented to the user's manager. It's also the
  product version of an earlier embedding study (`gemma-study`): "a shared audio–text embedding space used for
  something real".
- **Feature:** type a vibe → get 20-second moments with a play button and plain-word "why it matched" chips
  ("high energy · lots of laughter · topic: football"). "More like this" from any clip. A 2-D map of all clips.
- **It became a study** of how audio–text embeddings behave: what they capture, the modality gap, and why the
  textbook fix hurt.
- **Original plan:** `README.md` (phases 0–6). What changed and why: `PROJECT_STATUS.md` §3.

---

## 2. Models and how to run them (exact)

### EmbeddingGemma 2 (chosen)
- **Model:** `google/embeddinggemma-2` (Apache-2.0, 740M params: 270M text backbone + 300M audio encoder + 170M vision
  encoder), loaded via **sentence-transformers 6.1**, transformers 5.20, torch 2.14 CPU, on Python 3.14.
- **Output:** 768-d, L2-normalised (MRL truncation to 512/256/128 is supported but **was not tested**).
- **Load (audio + text):**
  `SentenceTransformer(path, device="cpu", config_kwargs={"vision_config": None}, model_kwargs={"dtype": torch.float32})`.
  For text only (queries), also pass `"audio_config": None`.
- **Audio input:** `{"array": float32 mono, "sampling_rate": 16000}`. The model card limit is about 327 s of audio per
  input; we used 20 s. Audio gets **no prompt**.
- **Text prompts** (the model is trained with task prefixes):
  - Queries and map words use `prompt_name="SearchQuery"` → "task: search result | query: …".
  - Transcripts (documents) are embedded as `"title: none | text: …"`.
- **Gotchas:**
  - It loads **bfloat16 by default, which is 12× slower** on a laptop CPU without native bf16 (33.9 s vs 2.7 s per
    20-s clip at batch 1). Force **float32**. **float16 gives NaNs** (per the model card).
  - It needs **pillow** and **torchvision** even for audio/text only (the processor loads its image/video parts).
- **Speed:** ~3.1 s per 20-s clip in fp32 with ~10 threads. Indexing 2,808 clips took ~3.9 h wall-clock, run in
  parallel with Whisper at 6 threads each, on a 12-core laptop.

### LAION-CLAP (compared, not used)
- **Model:** `laion/clap-htsat-unfused` via `transformers.ClapModel`; 48 kHz input, max 10 s, so each 20-s clip was
  split into **two 10-s windows, embedded, averaged and re-normalised** (deterministic, instead of the processor's
  random truncation). 512-d. ~0.37 s per clip (8× cheaper).

### Whisper (transcripts)
- **Model:** `Systran/faster-whisper-small`, int8, CPU, `beam_size=1`, `word_timestamps=True`, `vad_filter=True`,
  `language="en"`. ~5.5× real time with 12 threads. Words are assigned to a 20-s clip by word **midpoint**.

### LLM (query parsing only)
- **Model:** `gpt-5-mini` with `reasoning_effort: minimal` via an OpenAI-compatible gateway (URL in the uncommitted
  `config.local.yaml`). ~$0.0003 per new query, cached per normalised query. Daily spend guard $0.80. Total spend
  $0.0066.

---

## 3. Data and pipeline (exact)

- **Shows (39)**, chosen for vibe spread, not popularity (`data/feeds.yaml`):

| Vibe group | Shows |
|---|---|
| comedy chat | The Adam Buxton Podcast; SmartLess; Conan O'Brien Needs A Friend; Off Menu |
| sleep/meditation | Get Sleepy; Nothing Much Happens; Sleep With Me; Tara Brach |
| asmr/ambient | ASMR by GentleWhispering; ASMR For Sleep And Relaxation; Slow Radio; Relaxing Nature Sounds |
| true crime | Crime Junkie; Morbid; Casefile; Criminal |
| sports banter | The Totally Football Show; Football Daily; Men In Blazers; The Bill Simmons Podcast |
| news briefing | Up First; The Daily; Global News Podcast; The Journal |
| interview | Armchair Expert; Fresh Air; Desert Island Discs; WTF with Marc Maron |
| debate | Open to Debate; Left, Right & Center; The Rest Is Politics; Moral Maze |
| kids stories | Stories Podcast; Circle Round; The Story Seeds Podcast (Brains On! failed) |
| music-heavy | Dissect; All Songs Considered; Switched on Pop; Song Exploder |

- **Episodes:** the 3 most recent full episodes (≥ 10 min) per show = 117. Audio window **120–600 s** (skips intros
  and ads). **20-s clips, no overlap** → 2,808.
- **Pipeline** (CLI `vibe <step>`):
  `episodes → segments → embed --model gemma → transcribe → acoustic → textemb → evaluate → demo`.
  Outputs go to `index/` (gitignored): `segments.parquet`, `audio_emb.npy` (2808×768), `transcripts.parquet`,
  `acoustic.parquet`, `text_emb.npy`, `features.parquet`, `centering.npz`.
- **Getting the data:** a restrictive corporate proxy blocked the Hugging Face weight CDN and about half the podcast
  hosts. Everything was downloaded on another machine (`scripts/fetch_bundle.py`), moved as one zip, and verified
  against checksums (`scripts/import_bundle.py`). **No audio is ever hosted or published.** The page streams from
  the publishers' own links.

### Measured features (`src/vibe/features.py`)
All are per clip, then converted to **corpus percentiles (0–1)**:

| Feature | How |
|---|---|
| energy | Mean of the percentiles of RMS loudness (dB, non-silent frames) and its std. librosa RMS, frame 1024, hop 512 @ 16 kHz |
| pause_ratio | Share of frames more than **25 dB** below the episode's p95 frame loudness |
| expressiveness | std of pitch in semitones (librosa `yin`, 70–400 Hz) over frames within 15 dB of p95; octave errors (more than 12 semitones from the median) dropped. `pyin` was 12 s per clip, so `yin` was used instead |
| pace_wpm | Whisper words in the clip ÷ (20/60) |
| laughter / music / crowd | **Zero-shot:** cos(clip, positive prompt) − cos(clip, contrast prompt) |

**Zero-shot prompt pairs (final):**
- **laughter:** "a group of friends laughing out loud at a joke" vs "a person speaking seriously"
- **music:** "music playing" vs "people talking"
- **crowd:** "a live audience laughing and applauding" vs "a quiet studio recording"

**Feature sanity** (mean percentile per vibe group; this confirms the features track intuition):

| vibe | energy | express. | pace | pauses | music | laughter | crowd |
|---|---|---|---|---|---|---|---|
| asmr/ambient | 0.17 | 0.53 | 0.05 | 0.34 | 0.81 | 0.60 | 0.20 |
| sleep/meditation | 0.39 | 0.30 | 0.30 | 0.73 | 0.62 | 0.38 | 0.31 |
| comedy chat | 0.74 | 0.61 | 0.63 | 0.39 | 0.28 | **0.77** | 0.73 |
| sports banter | 0.46 | 0.44 | 0.74 | 0.56 | 0.38 | 0.55 | 0.69 |
| news briefing | 0.53 | 0.54 | 0.52 | 0.46 | 0.43 | 0.30 | 0.58 |
| music-heavy | 0.52 | 0.46 | 0.52 | 0.45 | 0.74 | 0.51 | 0.37 |
| kids stories | 0.56 | 0.68 | 0.42 | 0.57 | 0.60 | 0.58 | 0.40 |
| true crime | 0.59 | 0.51 | 0.56 | 0.48 | 0.47 | 0.51 | 0.42 |
| interview | 0.51 | 0.52 | 0.58 | 0.51 | 0.35 | 0.55 | 0.60 |
| debate | 0.55 | 0.46 | 0.65 | 0.53 | 0.35 | 0.26 | 0.66 |

(The music score is high for ASMR/ambient too: zero-shot "music" also fires on non-speech ambience.)

---

## 4. Search method (exact, `src/vibe/rank.py`, `src/vibe/query.py`)

- **Query parse:** one LLM call → JSON `{vibe_text, targets{feature: low|mid|high}, topic, avoid["feature:level"]}`.
  Invalid fields are **dropped** (not the whole parse); it retries once; it falls back to a keyword map; results are
  cached.
- **Score:** `0.4 · vibe + 0.4 · feature_fit + 0.2 · topic`, each part **min-max normalised per query**.
  - **vibe** = cosine(audio clip, normalise(embed(user's own words) + embed(LLM vibe_text))). Long LLM prose alone
    embedded poorly against audio, so the user's words are always included.
  - **feature_fit** = mean over targets of `1 − |pct − level|` (low 0.2, mid 0.5, high 0.8); `avoid` adds
    `|pct − level|`.
  - **topic** = cosine(topic text, transcript embedding), **set to 0 for clips with fewer than 15 transcript words.**
    Empty transcripts all collapse to one embedding, which happened to match "sports".
  - **Weights were never tuned.**
- **Selection:** at most 2 clips per show; adjacent clips (within 20 s) are merged.
- **"Why it matched" chips** come from the numbers, not an LLM.
- **More like this:** `0.6 · minmax(audio cos) + 0.4 · (1 − mean |pct diff|)`, excluding the seed's ±1 neighbours.
- **Map words:** the 25 clips with the highest raw audio cosine to the word (`rank.nearest_clips`).
- **Centring switch:** `rank.center` in `config.yaml` (0..1; currently **false/0**). See §7.

---

## 5. Evaluation protocols

### 5.1 Human listening test (the primary metric)
- **Design:** 12 long, descriptive demo searches (list in `reports/demo_queries.txt`) × the top 4 clips from the live
  search.
  - The rating page (`docs/rate.html`) shows the search text and auto-plays the exact 20-s clip from local disk.
    **Show names are hidden.** Clip order is shuffled within each search (seed 7).
  - Answers: **Y** matches / **N** doesn't / **U** not sure (U is excluded from scores; none were used).
- **One listener** (the project owner). **144 unique (search, clip) ratings** in total across 3 rounds:
  - **Round 1** (raw): 48.
  - **Round 2** (full centring): 27 new; the 21 unchanged (search, clip) pairs reused their round-1 ratings.
  - **Study round** (partial centring + short searches): 69 new; the variant was hidden and searches were shuffled
    (`docs/study.html`).
  - Ratings are pooled by (search, clip) key, so a pair is rated once and reused across variants.
  - Files: `reports/listening_test_v1.json`, `listening_test_centred.json`, `listening_study.json`.
- **Rating rules agreed mid-test** (important for comparability):
  - Judge the **sound**, not the topic or the show's category ("imagine hearing it with no idea what show it is").
  - **"music"** requires audible music; people *talking about* music = No.
  - **Whispering** requires an actual whisper or a breathy near-whisper; a soft, slow, voiced voice = No (consistent
    with round 1).
  - **The more specific the search, the stricter the match.** "news" = factual report-style delivery is enough;
    "serious news voice reading the headlines" = must sound like an anchor reading headlines, not true-crime
    narration.
  - **If the main feeling is missing, it's a No,** even if details match. "Heated argument" clips with overlapping
    talk but no hostility = No.
- **Limitations:** one listener, who also built the system; small n; **no random clips were rated, so there's no human
  chance baseline.**

### 5.2 Automatic category check (proxy; de-emphasised)
- **Design:** 8 searches with an obvious iTunes category ("sports talk" → Sports, …). The score is the share of the
  top 10 (max 10 per show) whose show category matches. Random baseline = the category's share of clips (mean 12.5%).
- **Why it's only a proxy:** categories describe the **show, not the 20 seconds**. It can't see laughter etc., and it
  rewards *topic* matches. It was effectively testing "predict the show category from its sound".

### 5.3 Same-show check
- **Design:** 50 random seed clips; "more like this" top 10; share of results from the seed's own show (excluding ±1
  neighbours).

### 5.4 Phase-1 model comparison
- **Design:** 15 prompts × 300 random clips (from an earlier 15-min, overlapping segmentation). The score is whether
  each top-5 clip came from a show in a fitting vibe group (a proxy).

---

## 6. Results (all numbers)

### 6.1 Listening test, raw embeddings (live search)

| Search | Matched (of 4) |
|---|---|
| two friends laughing about football, late-night energy | 4 |
| calm, slow, one voice, like a bedtime story | 4 |
| kids story with funny voices | 4 |
| excited fast talking about sports | 3 |
| serious news voice reading the headlines | 3 |
| dramatic storytelling about a murder | 3 |
| thoughtful slow interview about life | 3 |
| relaxed chat between comedians, lots of laughs | 3 |
| soft whispering, very quiet | 2 |
| upbeat music and singing | 2 |
| heated argument, people talking over each other | 1 |
| rain and nature sounds, no talking | 1 |
| **Total** | **33 / 48 (69%)** |

- **Grouped:**
  - **How people talk** (the first 8 rows): **27/32 (84%)**.
  - **Specific sounds** (whispering, music, rain): **5/12 (42%)**.
  - **Interaction** (argument): **1/4**.
- **By rank:** #1 8/12, #2 9/12, #3 7/12, #4 9/12, so **rank order within the top 4 is noise.**
- **Misses are near-misses:** "whispering" → soft bedtime voices (Nothing Much Happens); "rain" → calm ASMR/sleep
  clips; "heated argument" → overlapping but civil talk (Fresh Air, The Journal).

### 6.2 Short searches, raw (study round)
"laughter" 3, "music" 2, "sports" 4, "news" 4, "calm" 4, "whispering" 3, "rain" 1, "crime" 4, "a children's story" 2,
"football" 4 → **31/40 (78%)**.

### 6.3 Automatic category check (raw)

| Query → expected | random | sound only | features only | hybrid |
|---|---|---|---|---|
| calm guided relaxation → Health & Fitness | 15% | 70% | 60% | 70% |
| comedians joking around → Comedy | 15% | 90% | 50% | 90% |
| crime story narration → True Crime | 10% | 30% | 10% | 70% |
| sports talk → Sports | 10% | 60% | 10% | 100% |
| news headlines briefing → News | 15% | 100% | 50% | 80% |
| a bedtime story for children → Kids & Family | 8% | 0% | 0% | 0% |
| music with singing and instruments → Music | 10% | 40% | 30% | 60% |
| soft whispering to help you sleep → Health & Fitness | 15% | 90% | 0% | 100% |
| **mean** | **12.5%** | **60%** | **26%** | **71%** |

- **Sound does most of the work; features re-rank** (crime 30 → 70, sports 60 → 100).
- **Features alone are weak.**
- **"Bedtime story for children" = 0%:** it returns adult sleep stories (acoustically identical; a categorical miss).
- **History:** before the two ranking fixes (§4), the first 702-clip run scored 54% → 67% mean with them (the two
  fixes were not measured separately).

### 6.4 Same-show ("more like this")
Hybrid **58%**, sound only 54%, features only 23%, random 2.5%.

### 6.5 Phase-1 model comparison (top 5 from a fitting vibe group; random 13%)

| | CLAP | EmbeddingGemma 2 |
|---|---|---|
| overall | 51% | **70%** |
| prompts won | 3 | **8** |

Per prompt (CLAP / Gemma, of 5):
- laughing 5 / 3
- whispering 5 / 3
- calm soft voice 5 / 5
- one person speaking slowly 5 / 5
- quiet meditation 4 / 3
- rain & nature 3 / 5
- music playing 1 / 4
- guitar & singing 3 / 3
- news anchor 2 / **5**
- excited sports commentary 0 / **4**
- dramatic crime narration 1 / **4**
- storyteller to children 1 / 2
- friends chatting 1 / 2
- two people arguing 0 / 1
- (loud crowd: unscored; both returned ambient)

**CLAP wins on sound events (laughter, whispering); Gemma wins on speech styles and genres.**

### 6.6 Embedding-only word lookups (25 nearest clips by raw cosine)
- "a tense crime story": 23 true crime
- "a news anchor": 21 news
- "excited sports talk": 20 sports
- "whispering": 19 ASMR
- "a calm soothing voice": 15 sleep + 8 ASMR
- "people laughing": 14 comedy (spread out)
- "a storyteller reading to children": 13 sleep, 9 kids
- "rain and nature sounds": 25 ASMR/ambient
- "a crowd cheering" and "music playing": mostly ASMR (fail; this corpus has little of either)

---

## 7. The modality gap and the centring study (key findings for follow-up work)

### 7.1 The gap (measured)
- **Mean cosine of random pairs:** audio↔audio **0.705**, text↔text **0.687**, text↔audio **0.575**.
  - Text phrases = 77 neutral `GENERIC_PHRASES` in `src/vibe/centering.py`.
- **Joint UMAP** (clips + 77 phrases + 10 test words; n_neighbors 15, min_dist 0.15, cosine, seed 0): words form
  their **own island**.
  - **0/10** of a test word's 10 nearest 2-D neighbours are clips.
- **Search works anyway:** ranking only needs relative order; every clip pays a similar "crossing cost".

### 7.2 Centring (the textbook fix)
- **Formula:** `clip' = normalise(clip − s · mean(all clip vectors))`,
  `query' = normalise(query − s · mean(77 neutral phrases))`, strength s ∈ [0, 1].
  - Means are stored in `index/centering.npz`.
  - Two fixed vectors, one subtraction per query, so it's trivially real-time and scalable.
  - The text mean deliberately excludes all test searches (no tuning leak).
  - It was robust to the phrase set: using 16 test-ish words instead gave nearly identical effects.
- **Geometry:** after full centring, **7/10** of a word's nearest neighbours in the joint UMAP are clips. Words land in
  matching clusters ("news" by news shows, "football" by sports).
- **Category (proxy) improves:** of the 25 nearest clips, from the expected show type:
  - **up:** laughter 11 → 17, music 11 → 19, news 15 → 20, sports 15 → 21, calm voice 17 → 20,
    crime story 22 → 24, children's story 13 → 17, football 24 → 25
  - **down:** rain 25 → 23, **whispering 19 → 11**
  - The full-pipeline category check went 71% → 72%.
- **By ear it got worse** (pooled ratings):

| strength | 0 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---|---|---|---|---|
| 12 long searches (of 48) | **33** | 32 | 32 | **33** | **27** |
| 10 short searches (of 40) | **31** | | 28 | | **26** |
| category check | 71% | 72% | 72% | 72% | 72% |

- **Per long search** (s = 0 → 1):

| Search | 0 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---|---|---|---|---|
| football banter | 4 | 4 | 4 | 4 | 3 |
| bedtime | 4 | 4 | 4 | 4 | 4 |
| argument | 1 | 1 | 1 | 1 | 0 |
| whispering | 2 | 3 | 3 | 3 | 3 |
| excited sports | 3 | 3 | 2 | 2 | 0 |
| news voice | 3 | 2 | 3 | 4 | 4 |
| murder storytelling | 3 | 3 | 3 | 4 | 4 |
| rain | 1 | 0 | 0 | 0 | 0 |
| music & singing | 2 | 2 | 2 | 1 | 0 |
| slow interview | 3 | 3 | 3 | 3 | 3 |
| kids voices | 4 | 4 | 4 | 4 | 3 |
| comedians | 3 | 3 | 3 | 3 | 3 |

- **Per short search** (s = 0 / 0.5 / 1):

| Search | 0 | 0.5 | 1 |
|---|---|---|---|
| laughter | 3 | 3 | 3 |
| **music** | 2 | 1 | **0** |
| sports | 4 | 4 | 4 |
| news | 4 | 4 | 4 |
| calm | 4 | 4 | 4 |
| **whispering** | 3 | 2 | **1** |
| rain | 1 | 1 | 1 |
| crime | 4 | 4 | 4 |
| **a children's story** | 2 | 1 | **1** |
| football | 4 | 4 | 4 |

- **Pattern:**
  - **Sound-defined searches lose** (music, whispering, children's story, excited sports, music & singing).
  - **Topic-defined searches hold or gain** (news, crime/murder, sports, football, calm).
  - **Examples:** after centring, "music"/"upbeat music and singing" returned music-*talk* shows (Dissect, Song
    Exploder, Switched on Pop, Fresh Air); "excited sports talk" returned *calm* stretches of sports shows.
- **Decision:** live search uses raw embeddings (`rank.center: false`).

### 7.3 Interpretation (hypothesis, NOT proven)
- **Claim:** the shared mean direction(s) of each modality are not purely a "this is audio/text" tag. Part of what
  distinguishes clips *acoustically* (music vs speech, whisper vs voiced, energetic vs calm) appears to be correlated
  with those directions.
- **Mechanism:** subtracting the means and re-normalising re-weights the remaining dimensions toward **semantic/topic**
  content.
- **Consequence:** matching becomes more on-topic and less on-sound, which is good for category retrieval and bad for
  vibe retrieval.
- **Supporting evidence:** the pattern in §7.2; the zero-shot "music" score is high for ambient/ASMR clips, which
  suggests acoustic "non-speech-ness" lives along broad directions.
- **Untested.** See §9 for how to test it.

---

## 8. Findings catalogue (claims → evidence → confidence → implication)

| # | Finding | Evidence | Confidence | Implication for next project |
|---|---|---|---|---|
| F1 | Audio–text embeddings capture **speaking style and mood** well | 27/32 "how people talk" | Measured (1 listener) | Vibe search on speech audio is viable with raw embeddings, no training |
| F2 | Weak on **specific non-speech sounds** | 5/12; music/rain/whisper misses | Measured | Expect failures on sound events; add a sound-event model (CLAP) or a better corpus |
| F3 | Captures interaction **mechanics, not emotion** | "heated argument": overlap without hostility, 1/4 | Measured | Emotion/affect needs another signal (prosody model, text sentiment) |
| F4 | **CLAP vs Gemma are complementary** | CLAP wins laughter/whisper, Gemma wins speech genres (§6.5) | Measured (proxy) | Try an ensemble or score fusion |
| F5 | **Show/production identity** is strongly encoded | same-show 58% vs 2.5%; map clusters by show | Hypothesis on cause | Control for show (e.g. per-show centring, de-duplicate per show) when measuring "vibe" |
| F6 | **Top-k order is noise** | rank #1 8/12 vs #4 9/12 | Measured (small n) | Present results as a set; use a reranker if order matters |
| F7 | **Modality gap** exists | cos 0.705/0.687/0.575; 0/10 neighbours | Measured | Don't plot or threshold text and audio vectors on the same absolute scale without care |
| F8 | The gap **doesn't break ranking** | 33/48 with the gap | Measured | Absolute cosine values aren't comparable across modalities, but rankings are |
| F9 | **Centring hurts vibe** at full strength; partial gives nothing | §7.2 table | Measured | Don't centre for vibe retrieval; may help topic/category retrieval |
| F10 | Centring shifts matching **sound → topic** | per-search pattern, music-talk shows | Hypothesis | Test with projection experiments (§9) |
| F11 | **Proxy metrics mislead** for vibe | category check flat/up while ears fell | Measured | Always include a blind human listening test; treat category metrics as sanity only |
| F12 | **Zero-shot contrast choice matters** | laugh-vs-talk made ASMR > comedy; speech-vs-speech fixed it | Measured | Contrast prompts must hold modality and "speechiness" constant |
| F13 | **Long LLM prose embeds poorly** against audio | fixes lifted category 54% → 67% (with F14, not isolated) | Partly measured | Embed the user's words; use the LLM to *add*, not replace |
| F14 | **Empty inputs collapse** to one vector | 87 near-silent clips; Slow Radio topped "sports" | Measured | Gate any text-embedding signal on minimum content |
| F15 | **fp32 on CPU** (bf16 12× slower, fp16 NaN) | timings | Measured | Set the dtype explicitly |
| F16 | Even **one-word searches** work raw | 31/40 | Measured | Short queries don't need LLM expansion to work |

---

## 9. Open questions and suggested experiments (ranked)

1. **Why does centring hurt? Test F10:**
   - (a) Remove only the **top-k principal directions** of the gap (or only the projection on the mean-difference
     vector `mean_audio − mean_text`) instead of the full means.
   - (b) Measure how much of the zero-shot music/laughter scores or measured features is explained by each clip's
     projection on the mean direction.
   - (c) Centre only one side (audio or text).
   - Re-rate with the same protocol (ratings cache by (search, clip)).
2. **Human baseline:** add randomly chosen clips blind into the rating queue to get a chance rate; use **several
   listeners** and report agreement (Cohen's/Fleiss' kappa).
3. **Show confound (F5):** re-run "more like this" and searches with **per-show centring** (subtract each show's mean)
   to see what "vibe" remains beyond production.
4. **Model fusion (F4):** CLAP + Gemma score fusion; expect gains on sound-event searches.
5. **Ablate the query vector (F13):** user words only vs LLM description only vs both, by ear.
6. **Corpus coverage:** add shows with real music, nature sounds, live crowds and genuine arguments, to separate model
   gaps from data gaps (F2).
7. **MRL truncation:** does 256-d keep vibe quality? (4× smaller index.)
8. **Clip length:** 20 s was not tuned; 10 s or 30 s may change interaction/emotion results.

---

## 10. Reusable code and artifacts

| What | Where | Notes |
|---|---|---|
| Model wrappers (Gemma, CLAP) | `src/vibe/embed.py` | `Gemma(text_only=False)`, `.audio(clips)`, `.text(texts, prompt_name)`; resumable per-episode embedding |
| Centring | `src/vibe/centering.py` | `GENERIC_PHRASES`, `compute()`, `audio(x, strength)`, `text(x, strength)` |
| Ranking | `src/vibe/rank.py` | `score_all`, `search(q, k, strength=…)`, `like`, `nearest_clips(text, strength=…)` |
| Features | `src/vibe/features.py` | acoustic features, zero-shot pairs, percentiles |
| Query parser + LLM client | `src/vibe/query.py`, `src/vibe/llm.py` | lenient validation, keyword fallback, cache, spend guard |
| Listening-study tooling | `src/vibe/study.py`, `docs/rate.html`, `docs/study.html`, `POST /rate?name=` in `src/vibe/server.py` | blind queue, ratings pooled by (search, clip) |
| Gap plots | `src/vibe/demo.py::modality_gap_plots` | joint UMAP raw vs centred, neighbour metric, per-word lift |
| Offline data bundle | `scripts/fetch_bundle.py`, `scripts/import_bundle.py` | for proxy-restricted machines |
| Results page | `docs/index.html` (+ `data.js`) | GitHub Pages from `/docs`; the light/dark toggle is `docs/theme.js` |
| Explainer | `docs/explain.html` | intuitive explanations, toys, real-data charts |
| Raw results | `reports/*.json` | `listening_*.json`, `study_design.json`, `study_results.json`, `phase4_eval.json`, `phase1_smoke.json` |
| Config | `config.yaml` (+ uncommitted `config.local.yaml` for the LLM URL) | `rank.center`, weights, audio window |

**Not in git:** `models/`, `index/`, audio. Rebuild with the pipeline (§3) after importing the bundle. Tests: `pytest`
(12 tests: segmenting, ranking maths, query validation, spend guard).

---

## 11. Environment notes for a new machine

- Windows 11, Python 3.14 venv; all dependencies install from pip. A corporate TLS-inspecting proxy needs
  `truststore.inject_into_ssl()` (Python 3.13+ rejects the proxy CA otherwise).
- **The proxy blocks** the Hugging Face weight CDN and many podcast hosts. Use the offline bundle route. Also set
  `HF_HUB_OFFLINE=1`.
- Run long jobs detached; the demo server (`vibe serve`, 127.0.0.1:8765) must be restarted after a reboot.
- On the published page, free-text search, custom map words and rating need the local server; publisher audio may be
  blocked on the corporate network.

---

## 12. Recommendations for a follow-up project that relies on these findings

- **Use raw EmbeddingGemma 2 embeddings for "how it sounds" retrieval** on speech audio. Don't centre for vibe.
  Consider centring for topic/category retrieval.
- **Budget for human listening from day one:** blind, Y/N, fixed rating rules (§5.1), ratings cached by (query, item)
  so variants can be compared cheaply. Add random items for a baseline and use more than one listener.
- **Treat category/label proxies as sanity checks only;** they rewarded the wrong behaviour here.
- **Expect weaknesses** on non-speech sound events and emotional interaction; plan a complementary signal (CLAP,
  prosody, text sentiment).
- **Control for show/speaker identity** when claiming "vibe" similarity.
- **Engineering:** fp32 on CPU; pillow + torchvision installed; prompts (SearchQuery for queries); gate text signals on
  empty transcripts; embed the user's own words alongside any LLM expansion.
