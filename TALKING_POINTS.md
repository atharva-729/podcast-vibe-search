# Talking points: Vibe Search

The page explains itself. Say the intro, then let people read. Only speak up with the points below.

---

## Intro (about 45 seconds, before anyone scrolls)

- **The gap:** Spotify lets you search podcasts by *name* or *topic*, not by how they *sound*. You can't ask for
  "two friends laughing about football, late-night energy".
- **The trigger:** new embedding models (here, Google's EmbeddingGemma 2) put **audio and text in one shared
  space**. The *sound* of laughter and the *word* "laughter" become comparable vectors.
- **The question:** does that alone make vibe search work, with no labels, no classifiers and no training?
- **What I did:** 39 podcasts, 2,808 twenty-second clips, all embedded on a laptop. Then I **listened**: I rated the
  top results blind, without seeing the show names.
- **The answer:** mostly yes, for *how people talk*. And it turned into a study of how these embeddings behave,
  including a well-known fix that made things **worse**.

---

## Things the page won't tell them

### On the first screen
- **"33 of 48" is my own ears, not a metric.** Each clip was heard blind. That's the point of the project, so say it.
- The ‹ › arrows show 5 example searches, each with its listening score.

### On the map (section 01)
- **Nobody labelled anything.** The coloured clusters appear only because similar-sounding clips get similar vectors.
- Pressing a word button is the **raw embedding alone**: no LLM, no extra features. It's the purest demo of the idea.
- The clusters are partly **show identity** (same hosts, same mic). Part of what the model calls "vibe" is production.

### On the listening results (section 02)
- **Why there's no accuracy % from a benchmark:** the early automatic check scored results by each show's iTunes
  category. A category describes the *show*, not the 20 seconds, so it can't tell whether anyone is laughing.
  Listening is the only honest test of vibe.
- **"Heated argument":** clips had people talking over each other, but no hostility. The model picks up the
  *mechanics* of an argument (overlapping voices), not the *emotion*.
- **How I rated edge cases:** judge the sound, not the topic. "Music" needed audible music, not people talking about
  music. A soft, slow voice isn't whispering.

### On the gap (section 03): the most interesting part
- **The modality gap is a known property** of models like this (CLIP has it too). I measured it here: words sit on
  their own island.
- **Centring is the standard fix:** subtract each side's average vector. It's cheap and real-time (two fixed vectors),
  so it would scale to Spotify.
- **It closed the gap on the map, and made search worse by ear:** 33 → 27. I then tested 25/50/75% and short
  searches. **No setting helped.** It's a cliff at 100%, not a slope.
- **The surprise:** the automatic metric said centring was *fine or better*. Shipping on that metric would have
  made the product worse. **Only listening caught it.** This is the takeaway I'd stress.
- **Why (hypothesis, not proven):** the "average" direction seems to carry part of the *sound* character.
  Remove it and matching drifts to *topic*: "music" started returning shows that *talk about* music.

### On what we learned (section 04)
- The tags matter: **Measured** vs **Hypothesis** vs **Tried & failed**. I kept those separate on purpose.
- **Two models, opposite strengths:** CLAP (sound events) was better at laughter and whispering, EmbeddingGemma 2 at
  speech styles. A combination could beat either.

### On "Try it"
- On a static page only the examples work. **Typing your own search needs my laptop's local server** (an LLM call
  plus the model). Offer to demo it live if asked.

---

## If someone asks

- **Cost?** About 4 hours of laptop CPU to index everything; **under 1 cent** of LLM spend in total; no GPU.
- **Scale to Spotify?** Indexing is embarrassingly parallel (embed once per clip), and search is nearest-neighbour
  lookup, which vector databases do at billions of rows. Centring would also be trivial at scale, but it doesn't help.
- **Why only one listener?** Time. The fair next step is several listeners, with random clips mixed in blind to give
  a "chance" baseline.
- **Biggest weakness?** Specific sounds (music, rain, crowds) and real arguments, partly because these podcasts
  barely contain them. That's a data gap, not just a model gap.
- **Rights?** No audio is hosted. Clips stream from each publisher's own link. Third-party shows: internal prototype
  only.
- **What next?** More listeners; a corpus with real music, nature sounds and live crowds; and testing whether
  removing only the *main* gap direction (instead of the full average) keeps the vibe.
