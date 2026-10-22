# Vibe Search: where the project actually went

Context handoff for anyone (or any AI chat) picking this up. `README.md` is the **original build plan**; this file
describes **what was actually built, what changed, why, and where things stand**. Last updated 2026-10-22.

> **For a follow-up project that builds on this one's results, read [FINDINGS.md](FINDINGS.md) first:** every
> method, number, finding, hypothesis and open experiment in one self-contained briefing.

---

## 1. In one paragraph

Vibe Search lets you search podcasts by how they *sound* ("two friends laughing about football, late-night energy")
and returns timestamped 20-second clips with plain-word reasons and a play button. It is an internal innovation-team
prototype with a Spotify hook: Spotify offers no vibe search, and its audio-feature API is closed to new apps.
**The selling point is the embedding model.** EmbeddingGemma 2 (Google, open weights) maps audio and text into one
768-dimension space, so the sound of laughter lands near the words "people laughing". The project tests whether that
makes vibe search work. It runs end to end on a laptop CPU. The headline result is a human listening test: **33 of 48
top results sounded right to a listener.** The audience is mainly the user's manager.

## 2. Current status

- **All README phases 0–5 are built and working.** Phase 6 (extras) was not done.
- **Corpus:** 39 shows × 3 episodes × minutes 2–10 → **2,808 clips** (20 s each, no overlap), 15.6 h of audio.
- **Results page:** `docs/index.html`, redesigned around the embedding idea (section 7). Served by `vibe serve` at
  http://127.0.0.1:8765/.
- **Listening test:** done by the user. 33 of 48 matched; raw ratings are in `reports/listening_test.json`.
- **Full numbers:** `reports/REPORT.md`.
- **Git:** public repo https://github.com/atharva-729/podcast-vibe-search (`main`). It was pushed as one squashed
  commit after scrubbing company details: the LLM URL is in the uncommitted `config.local.yaml`, proxy vendor names
  were removed, and run scripts no longer contain user paths. The full local history is kept in the local-only
  branch `local-history`; don't push it. GitHub Pages: Settings → Pages → Deploy from branch `main`, folder
  `/docs` → https://atharva-729.github.io/podcast-vibe-search/. On Pages, free-text search, custom map words and
  the rating pages need `vibe serve`, and publisher audio may be blocked on the corporate network.
- **LLM spend:** $0.0066 in total.

## 3. How it diverged from the README plan

| README plan | What actually happened | Why |
|---|---|---|
| ~40 shows × 3 eps × first 15 min, 10 s overlap (~5,400 est.; really 10,409 segments) | 39 shows × 3 eps × **minutes 2–10, no overlap** (2,808 clips) | Time: the full plan was ~20 h of CPU. An evening demo first used 1 ep × min 2–8 (702 clips); an overnight run then expanded it. Minutes 2–10 skip intros and ads. |
| Download audio directly | Downloaded on the user's **personal laptop** with `scripts/fetch_bundle.py`, moved via Google Drive as `bundle.zip`, then verified and unpacked with `scripts/import_bundle.py` | The corporate web proxy blocks Megaphone, Simplecast, Art19, Spreaker, ad-tracking redirects (Podtrac, swap.fm, byspotify, pdst.fm, mgln.ai) **and** the Hugging Face weight CDN (`us.aws.cdn.hf.co`, `*.xethub.hf.co`). Proxy allow-listing was requested but will take a while. |
| Model choice: EmbeddingGemma 2 vs CLAP | **EmbeddingGemma 2 chosen** | 15-prompt test on 300 clips: 70% vs 51% top-5 from a fitting show type (random 13%); won 8 prompts to 3. It costs ~3.1 s per clip on CPU vs 0.37 s. |
| `pyin` pitch | `librosa.yin` | pyin took 12 s per clip; yin takes under 0.1 s. |
| `voices_est` (optional) | Skipped | Time; the README marked it optional. |
| Phase 4: category check as the evaluation | **De-emphasised. A human listening test is now the headline.** | The user pointed out that the category check uses iTunes *show* categories, which can't tell whether a *clip* has laughter etc. It effectively tested "predict the podcast category from the sound", which isn't the feature. The user then labelled 48 clips by ear. |
| "No manual labelling" | One small human listening test was added (48 clips) | It was the only direct test of whether clips sound right. |
| GitHub Pages demo | Local only (`vibe serve`) so far | No remote yet; also about half the publishers' audio is blocked on the office network, so local playback is needed there. |

## 4. Environment and gotchas (important for anyone running this)

- **Machine:** Windows 11 work laptop, 12-core CPU, no GPU. Shells: PowerShell and Git Bash.
- **Python 3.14** in `.venv`. All dependencies installed fine, including torch 2.14 CPU, transformers 5.20,
  sentence-transformers 6.1, faster-whisper 1.2.1 and librosa 1.0. `pip install -e .` provides the `vibe` CLI.
- **Corporate TLS inspection:** Python 3.13+ rejects the proxy's CA (VERIFY_X509_STRICT). The code uses
  `truststore.inject_into_ssl()` (in `llm.py`), and `scripts/download_models.py` does the same. pip works as-is.
- **Extra dependencies not in the README:** `pillow` and `torchvision`, because EmbeddingGemma 2's processor loads its
  image and video parts even when unused. `truststore` is also added.
- **EmbeddingGemma 2 must run in float32 on CPU.** It loads in bfloat16 by default, which is **12× slower** here. Never
  use fp16 (NaNs, per the model card). Load with `config_kwargs={"vision_config": None}` (audio and text) or also
  `"audio_config": None` (text only, for queries).
- **Models live in `models/`** (gitignored): `google--embeddinggemma-2`, `laion--clap-htsat-unfused` and
  `Systran--faster-whisper-small`. Run with `HF_HUB_OFFLINE=1`.
- **LLM:** an internal OpenAI-compatible LLM gateway (LLM Foundry); its URL lives in `config.local.yaml`
  (not committed). Copy that file when setting up a new machine, model **`gpt-5-mini`** with `reasoning_effort: minimal`, and the token in `LLMFOUNDRY_TOKEN` (sent as
  `Bearer <token>:vibe-search`). The spend guard is $0.80/day, logged in `runs/spend.json`. Calls are cached in
  `runs/cache/`.
- **Long jobs:** run them detached (`Start-Process`). The overnight run used `runs/overnight.sh`, which also blocks
  sleep via `SetThreadExecutionState`.
- **The demo server dies if the laptop restarts.** Restart it with `.venv\Scripts\vibe.exe serve`; its PID is in
  `runs/serve.pid`.
- **Headless screenshots:** Edge headless needs its own `--user-data-dir` while the user has Edge open, and the server
  must be running.
- **Voice:** `/voice` isn't available in this Claude Code setup. The user dictates with Windows `Win+H`. Expect
  rambling, dictated messages and interpret them charitably.

## 5. Pipeline and data

```
vibe episodes      data/bundle_episodes.json → data/episodes.parquet (117 eps; spares fill failed shows)
vibe segments      → index/segments.parquet (config: audio.window_s [120,600], hop 20, 3 eps/show)
vibe embed --model gemma   → index/audio_emb.npy (2808×768, L2-normalised; per-episode parts in index/parts/)
vibe transcribe    faster-whisper small int8 → index/transcripts.parquet (words, pace_wpm)
vibe acoustic      librosa → index/acoustic.parquet (energy mean/var, pause_ratio, expressiveness)
vibe textemb       transcript text embeddings → index/text_emb.npy; zero-shot scores; percentiles → index/features.parquet
vibe evaluate      → reports/phase3_search.md/json, reports/phase4_eval.md/json
vibe demo          UMAP + precomputed queries + map words + listening results → docs/data.js
vibe serve         local API + page (127.0.0.1:8765)
```

- **Source audio:** the trimmed first 15 min of each episode in its original codec, in `data/audio_cache/raw/`
  (gitignored). It is decoded on demand with ffmpeg at 16 kHz (Gemma, Whisper) or 48 kHz (CLAP).
- **Shows:** `data/feeds.yaml` (40 + 5 spares). Pardon My Take timed out and Brains On! returned 404; Football Daily
  (a spare) replaced the first, and kids' stories has 3 shows.
- **Rights:** derived data plus publisher URLs only. Audio is never hosted, and transcripts aren't shown on the page.
  Flag to Anand before any client-facing use.

## 6. How search works (`src/vibe/`)

- **`query.py`:** one LLM call → `{vibe_text, targets{feature: low|mid|high}, topic, avoid}`. Invalid fields are
  dropped rather than failing the whole parse. It retries once and falls back to a keyword map, cached per normalised
  query.
- **`features.py`:** energy (loudness and its variation), expressiveness (pitch spread, yin), pause_ratio (frames more
  than 25 dB below the episode's p95), pace_wpm (Whisper). **laughter/music/crowd are zero-shot:** the clip embedding's
  similarity to a positive prompt minus a contrast prompt. Laughter contrasts "a group of friends laughing out loud at
  a joke" with "a person speaking seriously". The first version contrasted "people laughing" with "people talking",
  which made ASMR score above comedy, so it was changed to compare speech with speech. Everything is converted to
  corpus percentiles.
- **`rank.py`:** `score = 0.4·vibe + 0.4·feature_fit + 0.2·topic`, with each part min-max normalised per query.
  - **vibe:** audio embeddings against the sum of the embeddings of *the user's own words* and the LLM's `vibe_text`.
    Long LLM descriptions embed poorly on their own.
  - **topic:** zeroed for clips with fewer than 15 transcript words. Empty transcripts all shared one embedding, which
    matched "sports".
  - **Results:** max 2 per show, with adjacent clips merged.
  - **Reasons:** "why" chips are generated from the numbers, not by an LLM.
  - **Other functions:** `like()` does more-like-this (audio + feature closeness); `nearest_clips(text)` is the pure
    embedding nearest neighbours used for the map words.
- **Weights were never tuned.** Three fixes (the laughter prompts, the topic gate, the user's words in the vibe
  vector) were made after seeing results from the first 702-clip run. The overnight run used the same code unchanged.

## 7. Results (as they stand)

**Headline: human listening test** (`docs/rate.html`). 12 demo queries × top 4 clips, played blind with no show name,
judged "sounds like the search?" by one listener (the user):

- **4/4:** football banter, calm bedtime story, kids' story with funny voices
- **3/4:** excited sports talk, serious news voice, dramatic murder storytelling, thoughtful slow interview, comedians chatting
- **2/4:** soft whispering, upbeat music and singing
- **1/4:** heated argument, rain and nature sounds
- **Total: 33/48 (69%).** By rank: #1 8/12, #2 9/12, #3 7/12, #4 9/12.
- **Caveats:** one listener, 48 clips, no random clips rated, so there is no human chance baseline.

**Why the failures happen:** data gaps. Almost no nature-sound shows, no real shouting matches (the debate shows are
civil), and little crowd noise or music. The nearest clips are therefore the wrong kind (often ASMR).

**Embedding sanity check (the "words on the map"):** the 25 clips nearest each phrase, using the embedding alone:

| Phrase | Nearest clips |
|---|---|
| a tense crime story | 23/25 true crime |
| a news anchor | 21/25 news |
| excited sports talk | 20/25 sports |
| whispering | 19/25 ASMR |
| a calm soothing voice | 15/25 sleep |
| people laughing | 14/25 comedy, spread out |
| a crowd cheering, music playing | mostly ASMR (fail; excluded from the page buttons) |

**Finding 2: the modality gap and centring** (`src/vibe/centering.py`, `rank.center` switch, currently **false**).

- **The gap:** in raw EmbeddingGemma 2 space, mean cosine is 0.71 clip↔clip, 0.69 text↔text, but 0.57 text↔clip.
  Projected jointly (UMAP), words form their own island: 0 of 10 of a word's nearest map neighbours are clips.
- **Centring:** subtract the catalogue's mean audio vector and the mean of 77 neutral `GENERIC_PHRASES` (not the
  test searches), then re-normalise. Words then sit among their clips (7 of 10 neighbours are clips). It's real-time
  friendly: two fixed vectors, one subtraction per query.
- **Category improves:** single words find the right show type more often ("music" 11 → 19 of the 25 nearest,
  "sports" 15 → 21, "laughter" 11 → 17; "whispering" 19 → 11 gets worse). The automatic category check rose too.
- **Vibe gets worse.** In listening test round 2 (`reports/listening_test_centred.json`; 21 unchanged clip ratings
  reused, 27 new clips rated), the score fell **33 → 27 of 48**. Centring pulls toward what shows are *about*:
  "upbeat music and singing" returned music *talk* shows (0/4), and "excited sports talk" returned calm stretches of
  sports shows (0/4). It helped news voices, crime storytelling and whispering.
- **Decision:** live search stays raw (`center: false`). The page presents this as a finding: "closing the gap finds
  the right shows, but loses the vibe"; only listening caught it.
- **The user's note on rating "heated argument":** clips had people talking over each other, but without hostility.
  These were rated No. Conclusion: the system finds the *mechanics* of interaction, not the *emotion*.

**Finding 3: the centring-strength study** (`src/vibe/study.py`; `vibe study-queue` builds a blind rating queue,
`docs/study.html` collects ratings into `reports/listening_study.json`, and `vibe study-results` scores it).

- **Design:** partial centring (`rank.center` accepts 0–1; `centering.audio/text(x, strength)`) tested at
  0/.25/.5/.75/1 on the 12 long demo searches and at 0/.5/1 on 10 short searches ("laughter", "music", "sports",
  "news", "calm", "whispering", "rain", "crime", "a children's story", "football"). That came to 144 pooled
  (search, clip) ratings; the user rated 69 new clips in the study round.
- **Long searches:** 33, 32, 32, 33, 27 of 48 (a cliff at 100%). **Short searches:** 31, 28, 26 of 40.
  **Category check:** flat at 71–72%.
- **Sound-defined searches lose under centring:** "music" 2 → 0, "whispering" 3 → 1, "a children's story"
  2 → 1. Topic searches stay at 4/4. Conclusion: **centring strips sound and keeps topic**, and the category metric
  can't see it.
- **Decision unchanged:** `rank.center: false`.
- **On the page:** in section 03, a line chart (listener score for long and short searches, plus the automatic check,
  against the share of the gap closed; y axis 40–90%), a short-search pip grid (pips are clickable to play), and a
  "what we learned" box.
- **Rating rules agreed with the user mid-test:** judge the sound, not the topic; "music" needs audible music;
  whispering needs a real or breathy whisper (soft, slow voice = No); specific searches are judged strictly; if the
  main feeling is missing, No.

**De-emphasised checks** (kept in `reports/REPORT.md`, removed from the page; the user calls them "irrelevant" to
the pitch):

- **Category check:** 71% of top-10 results come from the expected iTunes category, against 13% random. Sound only
  60%, features only 26%.
- **More-like-this:** 58% of results come from the same show, against 2% random.

## 8. The results page (`docs/index.html`) and the user's design feedback

**Design rules** are in `CLAUDE.md`, and they apply to any project. In short: a pitch for a busy executive; the
first screen shows the question/answer and about 4 bullets; data shown side by side; results drillable by click;
"not obvious" bullets; a self-explaining chart; then "That is the result. Everything below is the how." Rearrange
rather than delete. The references are https://atharva-729.github.io/clef-video-probe/ and
https://atharva-729.github.io/base64-image-probe/ (dark ink, Fraunces serif headings, IBM Plex, mono kickers).

**Feedback so far:**

- **Iteration 1** (a plain demo page): fine.
- **Iteration 2** (an executive pitch built on the 71% category check): the user found it wordy and not
  self-explanatory, and said the 71% numbers are irrelevant.
- **Iteration 3 (current):** focus on **embeddings**, minimal text, counts instead of percentages, aimed at the user's
  manager. The structure is:
  1. **The feature:** "Search podcasts by how they sound." An example search with its top 3 playable clips, and
     "33 of 48 top results sounded right to a listener".
  2. **Why it works now:** a flow strip (clip → EmbeddingGemma 2 → 768 numbers ← EmbeddingGemma 2 ← "people
     laughing") and the UMAP map of all clips. Word buttons light up each phrase's 25 nearest clips, and with the
     server running you can type your own word (`/near`). It opens on "a news anchor".
  3. **Does it work:** the listening-test grid (12 rows × 4 green/red squares, click to hear) and a works/fails pair.
  4. **Try it:** search box and example chips, sliders tucked under "Fine-tune", results with play buttons.
  5. **Below the line:** a 4-step "how it was built" strip (Cut, Embed, Search, Listen), stats, caveats.
- **Iteration 4, from the user's feedback on iteration 3:**
  - **Hero:** a carousel of 5 example searches with ‹ › arrows and a hand-drawn yellow "more examples" arrow; each
    example shows its listening pips.
  - **Audio plays in place:** ▶ becomes ⏸ on the row, with a progress line; there's no sticky bottom player.
  - **Technical wording:** "768-d", "cosine", "UMAP". The user said the audience is technical, so don't over-simplify.
  - **Listening grid grouped by kind of search,** with a highlighted conclusions box: how people talk 27/32,
    specific sounds 5/12, interaction 1/4, misses are near-misses, #1 is no better than #4.
  - **New section 03 "A finding about the space":** a before/after headline (33 vs 27 of 48), two joint UMAP plots
    (original: a ringed word island; centred: labelled words among clips), a per-word before/after bar table, and a
    "what this means" box.
  - **Section order:** feature → why it works (map + word buttons) → does it work (listening) → the gap → try it →
    (below the line) how it was built → caveats.
- **Iteration 5 (current):**
  - **The study (section 03):** the centring-strength study added inside it (line chart + short-search pip grid +
    "what we learned").
  - **Legends beside the maps:** the vibe map and the gap plots each have a vertical colour key next to them.
  - **New section 04 "What we learned about the model":** 14 finding cards in 3 groups (good/bad at; the gap and
    centring; lessons), each tagged Measured / Tried & failed / Hypothesis / Lesson. These mirror `FINDINGS.md` §8.
  - **Hero:** a line framing the project as a study too, with a link down. The "more examples" hint arrow and the
    leftover now-playing ring on the map were removed at the user's request.
  - **Light/dark toggle** on both pages (`docs/theme.js`; the choice is saved; `?theme=light|dark` overrides).
  - **Section order now:** feature → 01 why it works → 02 does it work → 03 the gap + study → 04 what we learned →
    05 try it → (below the line) 06 how it was built → 07 caveats. Nav has an "Explainer ↗" link.
  - **Pending:** the user said "some changes to be made later", not yet specified.

**Other artefacts:**

- `docs/rate.html` / `docs/study.html`: the listening-test pages. They post ratings to `/rate?name=…`, which writes
  `reports/listening_<name>.json`.
- `docs/explain.html`: a fun, interactive explainer of every technical idea (embeddings, cosine, multimodal,
  contrastive training, UMAP, evaluation, modality gap, centring, every demo chart), with draggable toys, real-data
  charts, yellow annotation arrows, a quiz and a glossary.
- `TALKING_POINTS.md`: the presentation. The page is meant to be self-explanatory, so this has a 45-second intro plus
  only the non-obvious points per section, and a Q&A list.
- `FINDINGS.md`: the detailed findings/context briefing for follow-up projects.

## 9. Open items and next steps

- **The user plans more page changes later** (not yet specified). GitHub Pages needs to be switched on by the user
  (Settings → Pages → `main` / `/docs`).
- **A follow-up project relies on these findings;** hand it `FINDINGS.md`.
- **Partial centring and short-query centring were tested (Finding 3); neither helps by ear.** Possible next
  questions:
  - Why does the mean direction carry sound character? E.g. project out only the top principal direction of the gap
    instead of the full mean.
  - A larger, multi-listener test with random clips mixed in, for a chance baseline.
  - More corpus coverage for sound-defined vibes (music, nature sounds, live crowds).
- **A fairer listening test:** several listeners, with random clips mixed in blind to give a chance baseline.
- **Fill data gaps** (nature sounds, crowd/live audiences, real arguments, music) if those vibes matter.
- **GitHub remote and Pages:** needs a repo URL or the `gh` CLI, and a decision on visibility (Pages on a private repo
  needs a paid plan).
- **Optional:** the full 15-min windows / all 117 episodes at overlap (~20 h CPU); README Phase 6 extras (vibe drift,
  music mode, show vibe cards).
- **Housekeeping:** `bundle.zip` (4.7 GB) can be deleted from the repo root and from Google Drive. `runs/v1/` holds a
  snapshot of the earlier 702-clip demo.

## 10. Working with this user

- **Wants results fast and end-to-end:** bare-bones over polish, with progress updates during long runs, and parallel
  work where possible.
- **Wants discussion before big redesigns.** Explain plans in plain language; the user said "I don't understand
  anything" about jargon-heavy text.
- **Values honesty about weak evidence:** the user spotted that the category check doesn't test the feature.
- **Is on a corporate network with a restrictive proxy:** don't try to bypass it; route around it legitimately (as
  with the personal-laptop bundle).

## 11. File map

```
README.md                original build plan (phases, rules)    PROJECT_STATUS.md  this file
CLAUDE.md                results-page design rules              config.yaml        paths, models, LLM, audio window, weights
data/feeds.yaml          45 feeds                               data/episodes.parquet
scripts/fetch_bundle.py  offline downloader (personal laptop)   scripts/import_bundle.py  verify + unpack bundle.zip
scripts/LAPTOP_STEPS.txt instructions for the bundle            scripts/download_models.py (blocked here by proxy)
src/vibe/                cli, config, cache, llm, feeds, audio, embed, transcribe, features, textemb, query, rank,
                         evaluate, phase1, demo, server
docs/index.html, data.js results page                           docs/rate.html     listening test
docs/explain.html        fun, interactive explainer of every technical idea (embeddings, cosine, multimodal,
                         UMAP, modality gap, centring, evaluation, every demo chart) built on the real data;
                         linked from the demo nav ("Explainer")                 docs/study.html    study rating page
reports/REPORT.md        all numbers                            reports/listening_test.json  human ratings
reports/phase1_smoke.md  model pick; phase1_listen/ (150 clips, gitignored)
reports/phase3_search.md demo query results                     reports/phase4_eval.md  category + same-show checks
tests/                   12 tests (segmenting, ranking maths, query validation, spend guard)
runs/                    spend.json, logs, overnight.sh, v1/ snapshot
```
