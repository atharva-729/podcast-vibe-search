# Phase 1 smoke test: 15 prompts x 300 random segments

`hit` = top result's show is in a vibe group that fits the prompt (rough proxy only; listen to judge).

| | CLAP | EmbeddingGemma 2 |
|---|---|---|
| vibe hit rate (top-5, 14 scored prompts) | 51% | 70% |
| random baseline | 13% | 13% |
| prompts won (higher hit rate) | 3 | 8 |
| embed time per segment (CPU) | 0.37 s | 3.12 s |
| compute per hour of segment audio | 1 min | 9 min |

## people laughing
expected vibes: comedy chat · random baseline 7%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | ✅ Conan O’Brien Needs A Friend @11:40 (0.316) | ✅ Off Menu with Ed Gamble and Ja @04:40 (0.66) |
| 2 | ✅ Conan O’Brien Needs A Friend @05:50 (0.218) | ✅ Conan O’Brien Needs A Friend @11:40 (0.656) |
| 3 | ✅ Conan O’Brien Needs A Friend @10:50 (0.203) | ✅ Conan O’Brien Needs A Friend @14:30 (0.639) |
| 4 | ✅ SmartLess @07:00 (0.184) | · All Songs Considered @08:20 (0.638) |
| 5 | ✅ Off Menu with Ed Gamble and Ja @04:40 (0.166) | · Armchair Expert with Dax Shepa @01:50 (0.636) |

## calm soft voice
expected vibes: sleep/meditation, asmr/ambient · random baseline 20%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | ✅ Tara Brach @10:30 (0.378) | ✅ Nothing much happens: bedtime  @06:20 (0.727) |
| 2 | ✅ ASMR by GentleWhispering @11:40 (0.26) | ✅ ASMR by GentleWhispering @10:30 (0.696) |
| 3 | ✅ ASMR by GentleWhispering @10:30 (0.223) | ✅ Get Sleepy: stories for sleep @07:40 (0.683) |
| 4 | ✅ ASMR by GentleWhispering @01:50 (0.216) | ✅ ASMR by GentleWhispering @12:50 (0.683) |
| 5 | ✅ Get Sleepy: stories for sleep @07:40 (0.196) | ✅ ASMR by GentleWhispering @11:40 (0.681) |

## loud crowd
expected vibes: (not scored)

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | · Slow Radio @04:30 (0.141) | · Slow Radio @03:20 (0.695) |
| 2 | · Slow Radio @03:20 (0.136) | · Slow Radio @04:30 (0.675) |
| 3 | · Relaxing Nature Sounds @03:40 (0.096) | · Slow Radio @13:40 (0.671) |
| 4 | · Slow Radio @13:40 (0.089) | · Slow Radio @02:10 (0.667) |
| 5 | · Relaxing Nature Sounds @01:30 (0.068) | · Relaxing Nature Sounds @05:50 (0.657) |

## music playing
expected vibes: music-heavy · random baseline 12%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | · Casefile True Crime @03:40 (0.291) | ✅ Song Exploder @13:00 (0.66) |
| 2 | ✅ Song Exploder @13:00 (0.283) | ✅ Song Exploder @13:40 (0.645) |
| 3 | · Get Sleepy: stories for sleep @07:40 (0.281) | ✅ Switched on Pop @12:40 (0.641) |
| 4 | · Crime Junkie @01:10 (0.279) | ✅ Switched on Pop @02:10 (0.634) |
| 5 | · The Story Seeds Podcast @04:00 (0.275) | · Fresh Air @06:10 (0.632) |

## one person speaking slowly
expected vibes: sleep/meditation, asmr/ambient · random baseline 20%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | ✅ Tara Brach @10:30 (0.511) | ✅ Nothing much happens: bedtime  @13:00 (0.732) |
| 2 | ✅ Nothing much happens: bedtime  @13:00 (0.312) | ✅ ASMR by GentleWhispering @01:20 (0.714) |
| 3 | ✅ Nothing much happens: bedtime  @06:20 (0.31) | ✅ ASMR by GentleWhispering @01:50 (0.714) |
| 4 | ✅ ASMR by GentleWhispering @11:40 (0.307) | ✅ ASMR by GentleWhispering @10:30 (0.708) |
| 5 | ✅ Nothing much happens: bedtime  @04:30 (0.301) | ✅ ASMR by GentleWhispering @08:00 (0.708) |

## two people arguing
expected vibes: debate · random baseline 10%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | · All Songs Considered @08:20 (0.645) | · Slow Radio @03:20 (0.654) |
| 2 | · Men In Blazers @10:00 (0.57) | · The Journal. @05:10 (0.648) |
| 3 | · Conan O’Brien Needs A Friend @11:40 (0.527) | ✅ Moral Maze @12:50 (0.647) |
| 4 | · Morbid @07:50 (0.512) | · Slow Radio @13:40 (0.64) |
| 5 | · Football Daily @09:00 (0.511) | · SmartLess @13:50 (0.637) |

## whispering
expected vibes: asmr/ambient · random baseline 10%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | ✅ ASMR by GentleWhispering @11:40 (0.56) | · Tara Brach @10:30 (0.695) |
| 2 | ✅ ASMR by GentleWhispering @00:40 (0.535) | ✅ ASMR by GentleWhispering @12:50 (0.687) |
| 3 | ✅ ASMR by GentleWhispering @10:30 (0.533) | ✅ ASMR by GentleWhispering @10:30 (0.679) |
| 4 | ✅ ASMR For Sleep And Relaxation @09:00 (0.472) | · Nothing much happens: bedtime  @06:20 (0.679) |
| 5 | ✅ ASMR by GentleWhispering @12:50 (0.449) | ✅ ASMR For Sleep And Relaxation @14:00 (0.675) |

## rain and nature sounds
expected vibes: asmr/ambient · random baseline 10%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | ✅ Relaxing Nature Sounds @09:20 (0.396) | ✅ Relaxing Nature Sounds @07:00 (0.71) |
| 2 | ✅ Relaxing Nature Sounds @01:00 (0.396) | ✅ Relaxing Nature Sounds @01:00 (0.702) |
| 3 | ✅ Relaxing Nature Sounds @07:00 (0.38) | ✅ Relaxing Nature Sounds @09:20 (0.698) |
| 4 | · Get Sleepy: stories for sleep @02:40 (0.327) | ✅ Relaxing Nature Sounds @02:10 (0.697) |
| 5 | · Get Sleepy: stories for sleep @04:00 (0.309) | ✅ Relaxing Nature Sounds @01:10 (0.695) |

## a storyteller reading a story to children
expected vibes: kids stories · random baseline 10%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | ✅ The Story Seeds Podcast @04:00 (0.395) | · Get Sleepy: stories for sleep @02:40 (0.683) |
| 2 | · Open to Debate @09:30 (0.393) | ✅ Stories Podcast: A Bedtime Sho @00:10 (0.668) |
| 3 | · Open to Debate @13:20 (0.384) | · Nothing much happens: bedtime  @04:30 (0.662) |
| 4 | · Song Exploder @14:20 (0.382) | · Fresh Air @09:20 (0.655) |
| 5 | · The Daily @01:10 (0.372) | ✅ Circle Round @01:50 (0.65) |

## a news anchor reading the headlines
expected vibes: news briefing · random baseline 11%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | · Fresh Air @00:50 (0.38) | ✅ Up First from NPR @08:20 (0.67) |
| 2 | · Moral Maze @00:20 (0.366) | ✅ Up First from NPR @06:30 (0.661) |
| 3 | ✅ The Journal. @06:40 (0.359) | ✅ Up First from NPR @08:40 (0.655) |
| 4 | · All Songs Considered @08:10 (0.354) | ✅ The Daily @04:50 (0.655) |
| 5 | ✅ The Daily @01:10 (0.336) | ✅ Up First from NPR @11:00 (0.649) |

## excited sports commentary
expected vibes: sports banter · random baseline 11%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | · The Journal. @08:40 (0.478) | · Armchair Expert with Dax Shepa @00:40 (0.709) |
| 2 | · Open to Debate @07:30 (0.474) | ✅ The Totally Football Show with @06:30 (0.698) |
| 3 | · All Songs Considered @07:40 (0.458) | ✅ The Totally Football Show with @01:10 (0.697) |
| 4 | · Open to Debate @09:30 (0.454) | ✅ The Bill Simmons Podcast @04:40 (0.689) |
| 5 | · Stories Podcast: A Bedtime Sho @08:10 (0.449) | ✅ Football Daily @01:40 (0.689) |

## quiet meditation with long pauses
expected vibes: sleep/meditation · random baseline 9%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | ✅ Tara Brach @10:30 (0.372) | ✅ Nothing much happens: bedtime  @06:20 (0.696) |
| 2 | ✅ Get Sleepy: stories for sleep @07:40 (0.188) | ✅ Get Sleepy: stories for sleep @07:40 (0.695) |
| 3 | ✅ Get Sleepy: stories for sleep @04:00 (0.186) | · Casefile True Crime @03:40 (0.678) |
| 4 | · ASMR by GentleWhispering @01:20 (0.182) | ✅ Get Sleepy: stories for sleep @09:00 (0.664) |
| 5 | ✅ Get Sleepy: stories for sleep @02:40 (0.172) | · ASMR by GentleWhispering @08:00 (0.664) |

## dramatic narration of a crime
expected vibes: true crime · random baseline 9%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | · Moral Maze @00:20 (0.536) | ✅ Casefile True Crime @10:40 (0.683) |
| 2 | · Song Exploder @01:10 (0.52) | ✅ Criminal @01:20 (0.681) |
| 3 | ✅ Crime Junkie @07:20 (0.503) | ✅ Crime Junkie @04:30 (0.68) |
| 4 | · The Story Seeds Podcast @04:00 (0.502) | · Get Sleepy: stories for sleep @14:00 (0.679) |
| 5 | · Get Sleepy: stories for sleep @04:00 (0.496) | ✅ Crime Junkie @07:20 (0.675) |

## friends chatting casually
expected vibes: comedy chat, sports banter, interview · random baseline 29%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | · Circle Round @08:00 (0.157) | ✅ Conan O’Brien Needs A Friend @14:30 (0.681) |
| 2 | · Tara Brach @10:30 (0.146) | · The Story Seeds Podcast @05:50 (0.671) |
| 3 | · All Songs Considered @08:20 (0.132) | · Morbid @07:50 (0.671) |
| 4 | · ASMR by GentleWhispering @11:40 (0.127) | · Moral Maze @12:50 (0.663) |
| 5 | ✅ Conan O’Brien Needs A Friend @11:40 (0.126) | ✅ Fresh Air @13:20 (0.659) |

## guitar and singing
expected vibes: music-heavy · random baseline 12%

| # | CLAP | EmbeddingGemma 2 |
|---|---|---|
| 1 | · Up First from NPR @00:40 (0.418) | ✅ Song Exploder @11:40 (0.692) |
| 2 | ✅ Song Exploder @01:50 (0.412) | ✅ Song Exploder @13:00 (0.673) |
| 3 | ✅ Song Exploder @10:30 (0.379) | ✅ Song Exploder @01:50 (0.66) |
| 4 | · Circle Round @08:00 (0.349) | · ASMR For Sleep And Relaxation @09:00 (0.655) |
| 5 | ✅ Song Exploder @13:00 (0.345) | · Fresh Air @06:10 (0.652) |
