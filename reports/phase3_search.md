# Phase 3: demo queries (top 5)

## two friends laughing about football, late-night energy
parsed (llm): vibe_text='two close friends bantering and laughing together with a warm, late-night, high-energy tone; voices are animated, slightly husky from late hour, frequent overlapping chuckles and informal conversational rhythm, occasional exclamations and playful teasing; background is intimate rather than noisy.' targets={'energy': 'high', 'expressiveness': 'high', 'pace_wpm': 'mid', 'laughter_score': 'high'} topic='football' avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Football Daily | 6:40 | 0.899 | 0.84 / 0.91 / 1.00 | high energy · lots of laughter · expressive voices · topic: football |
| 2 | Men In Blazers | 5:00 | 0.859 | 0.87 / 0.83 / 0.90 | expressive voices · high energy · lots of laughter · topic: football |
| 3 | Off Menu with Ed Gamble and Jame | 9:20 | 0.826 | 0.88 / 0.91 / 0.55 | high energy · expressive voices · medium pace |
| 4 | Football Daily | 5:20 | 0.824 | 0.75 / 0.85 / 0.91 | medium pace · lots of laughter · expressive voices · topic: football |
| 5 | Armchair Expert with Dax Shepard | 4:20 | 0.813 | 1.00 / 0.81 / 0.44 | medium pace · expressive voices · lots of laughter |

## calm, slow, one voice, like a bedtime story
parsed (llm): vibe_text='single gentle voice, whispery/soft timbre, warm and soothing, minimal background sound, intimate lullaby-like ambience' targets={'energy': 'low', 'expressiveness': 'mid', 'pace_wpm': 'low', 'pause_ratio': 'high', 'music_score': 'low'} topic=None avoid=['music_score:high', 'energy:high', 'crowd_score:high', 'laughter_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Get Sleepy: stories for sleep | 5:20 | 0.619 | 1.00 / 0.55 / 0.00 | slow pace · lots of pauses |
| 2 | Nothing much happens: bedtime st | 9:00 | 0.57 | 0.69 / 0.73 / 0.00 | slow pace · no music · low energy |
| 3 | Nothing much happens: bedtime st | 5:40 | 0.569 | 0.74 / 0.68 / 0.00 | low energy · slow pace · lots of pauses |
| 4 | Get Sleepy: stories for sleep | 4:20 | 0.556 | 0.82 / 0.57 / 0.00 | slow pace · medium voices |
| 5 | ASMR by GentleWhispering | 3:20 | 0.543 | 0.65 / 0.71 / 0.00 | medium voices · slow pace · low energy |

## heated argument, people talking over each other
parsed (llm): vibe_text='confrontational, tense voices overlapping and interrupting each other; raised volume, sharp tone, quick exchanges, occasional shouting and breathy interjections' targets={'energy': 'high', 'expressiveness': 'high', 'pause_ratio': 'low', 'laughter_score': 'low', 'crowd_score': 'high'} topic=None avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Fresh Air | 6:20 | 0.696 | 0.94 / 0.80 / 0.00 | expressive voices · few pauses · no laughter |
| 2 | Fresh Air | 8:00 | 0.684 | 0.98 / 0.73 / 0.00 | few pauses · expressive voices · crowd noise |
| 3 | The Journal. | 9:00 | 0.657 | 0.87 / 0.78 / 0.00 | crowd noise · no laughter · high energy |
| 4 | Slow Radio | 4:20 | 0.647 | 1.00 / 0.62 / 0.00 | crowd noise · few pauses |
| 5 | The Journal. | 2:20 | 0.646 | 0.84 / 0.77 / 0.00 | few pauses · high energy · expressive voices |

## soft whispering, very quiet
parsed (llm): vibe_text='very soft whispering, intimate and hushed voice, breathy tones, minimal background noise' targets={'energy': 'low', 'expressiveness': 'mid', 'pause_ratio': 'high'} topic=None avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | ASMR by GentleWhispering | 7:40 | 0.72 | 0.95 / 0.85 / 0.00 | medium voices · low energy · lots of pauses |
| 2 | Nothing much happens: bedtime st | 5:40 | 0.701 | 0.92 / 0.83 / 0.00 | low energy · lots of pauses |
| 3 | ASMR by GentleWhispering | 9:40 | 0.694 | 0.96 / 0.77 / 0.00 | lots of pauses |
| 4 | Nothing much happens: bedtime st | 8:40 | 0.691 | 0.83 / 0.89 / 0.00 | low energy · medium voices · lots of pauses |
| 5 | Get Sleepy: stories for sleep | 2:40 | 0.688 | 1.00 / 0.72 / 0.00 | lots of pauses |

## excited fast talking about sports
parsed (llm): vibe_text='energetic, enthusiastic voices with noticeable pitch variation and quick delivery; occasional short laughs or exclamations; minimal background noise' targets={'energy': 'high', 'expressiveness': 'high', 'pace_wpm': 'high', 'laughter_score': 'mid'} topic='sports' avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Men In Blazers | 3:40 | 0.833 | 0.81 / 0.86 / 0.83 | fast pace · expressive voices · medium laughter · topic: sports |
| 2 | The Bill Simmons Podcast | 6:00 | 0.833 | 0.85 / 0.80 / 0.85 | fast pace · high energy · expressive voices · topic: sports |
| 3 | The Bill Simmons Podcast | 5:00 | 0.825 | 0.75 / 0.83 / 0.96 | fast pace · expressive voices · medium laughter · topic: sports |
| 4 | Men In Blazers | 5:00 | 0.81 | 0.76 / 0.84 / 0.85 | fast pace · expressive voices · medium laughter · topic: sports |
| 5 | The Totally Football Show with J | 4:00 | 0.795 | 0.76 / 0.79 / 0.88 | medium laughter · expressive voices · high energy · topic: sports |

## serious news voice reading the headlines
parsed (llm): vibe_text='Calm, authoritative, and neutral news anchor voice with clear diction, steady pacing, minimal emotive inflection, low background ambience.' targets={'energy': 'mid', 'expressiveness': 'low', 'pace_wpm': 'mid', 'pause_ratio': 'mid', 'music_score': 'low', 'laughter_score': 'low', 'crowd_score': 'low'} topic='news' avoid=['music_score:high', 'laughter_score:high', 'expressiveness:high', 'crowd_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Up First from NPR | 3:00 | 0.806 | 0.90 / 0.67 / 0.90 | flat delivery · no crowd · no laughter · topic: news |
| 2 | Up First from NPR | 5:40 | 0.782 | 0.96 / 0.56 / 0.86 | no laughter · medium pauses · no crowd · topic: news |
| 3 | Criminal | 5:20 | 0.773 | 0.86 / 0.70 / 0.73 | medium pace · no laughter · flat delivery · topic: news |
| 4 | Global News Podcast | 6:40 | 0.773 | 0.81 / 0.73 / 0.79 | flat delivery · no crowd · medium pauses · topic: news |
| 5 | Global News Podcast | 5:40 | 0.764 | 0.89 / 0.66 / 0.74 | medium pace · medium energy · no laughter · topic: news |

## dramatic storytelling about a murder
parsed (llm): vibe_text='deep, resonant voice with deliberate pacing and strong emotional inflection; tense, slow-building atmosphere with sparse ambient textures and dark, cinematic undertone; occasional breaths and soft pauses to heighten suspense' targets={'energy': 'mid', 'expressiveness': 'high', 'pace_wpm': 'low', 'pause_ratio': 'high', 'music_score': 'mid'} topic='murder' avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Fresh Air | 6:20 | 0.874 | 0.99 / 0.74 / 0.91 | expressive voices · medium energy · slow pace · topic: murder |
| 2 | Nothing much happens: bedtime st | 7:00 | 0.863 | 0.89 / 0.92 / 0.69 | slow pace · medium music · medium energy · topic: murder |
| 3 | Casefile True Crime | 5:20 | 0.848 | 1.00 / 0.62 / 1.00 | medium music · slow pace · topic: murder |
| 4 | Crime Junkie | 7:40 | 0.843 | 0.79 / 0.91 / 0.81 | medium music · expressive voices · slow pace · topic: murder |
| 5 | Crime Junkie | 8:00 | 0.838 | 0.92 / 0.74 / 0.86 | medium energy · lots of pauses · topic: murder |

## rain and nature sounds, no talking
parsed (llm): vibe_text='gentle ambient rain and natural outdoor sounds, no human voices, calm and immersive, soft water and rustling leaves' targets={'energy': 'low', 'expressiveness': 'low', 'pause_ratio': 'high', 'music_score': 'low', 'crowd_score': 'low', 'laughter_score': 'low'} topic=None avoid=['expressiveness:high', 'music_score:high', 'laughter_score:high', 'crowd_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Get Sleepy: stories for sleep | 6:00 | 0.644 | 0.93 / 0.68 / 0.00 | no laughter · lots of pauses · flat delivery |
| 2 | ASMR by GentleWhispering | 9:40 | 0.643 | 0.92 / 0.68 / 0.00 | no laughter · no crowd · flat delivery |
| 3 | ASMR by GentleWhispering | 7:00 | 0.621 | 0.92 / 0.64 / 0.00 | flat delivery · no crowd · no laughter |
| 4 | Relaxing Nature Sounds | 9:00 | 0.6 | 1.00 / 0.50 / 0.00 | no crowd · low energy · flat delivery |
| 5 | Get Sleepy: stories for sleep | 9:20 | 0.598 | 0.91 / 0.58 / 0.00 | flat delivery · no crowd |

## upbeat music and singing
parsed (llm): vibe_text='bright, energetic, rhythmic with melodic vocals and prominent upbeat instrumentation' targets={'energy': 'high', 'expressiveness': 'high', 'music_score': 'high', 'laughter_score': 'low'} topic=None avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Stories Podcast: A Bedtime Show  | 2:40 | 0.653 | 1.00 / 0.63 / 0.00 | expressive voices · music |
| 2 | The Story Seeds Podcast | 5:40 | 0.621 | 0.71 / 0.84 / 0.00 | music · expressive voices · no laughter |
| 3 | Switched on Pop | 6:00 | 0.597 | 0.63 / 0.86 / 0.00 | music · no laughter · expressive voices |
| 4 | ASMR by GentleWhispering | 5:40 | 0.593 | 0.61 / 0.87 / 0.00 | music · no laughter · expressive voices |
| 5 | Circle Round | 2:20 | 0.593 | 0.64 / 0.84 / 0.00 | music · high energy · expressive voices |

## thoughtful slow interview about life
parsed (llm): vibe_text='calm, intimate conversation with warm, reflective voices; gentle low background hum or soft ambient pad; minimal production so speech feels close and personal' targets={'energy': 'low', 'expressiveness': 'mid', 'pace_wpm': 'low', 'pause_ratio': 'high', 'music_score': 'low'} topic='life' avoid=['music_score:high', 'energy:high', 'laughter_score:high', 'crowd_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Get Sleepy: stories for sleep | 8:00 | 0.799 | 0.98 / 0.66 / 0.71 | slow pace · lots of pauses · topic: life |
| 2 | Fresh Air | 9:40 | 0.785 | 0.85 / 0.67 / 0.89 | low energy · lots of pauses · slow pace · topic: life |
| 3 | Tara Brach | 7:00 | 0.778 | 0.81 / 0.75 / 0.76 | slow pace · no music · low energy · topic: life |
| 4 | Tara Brach | 2:40 | 0.759 | 0.80 / 0.71 / 0.78 | slow pace · low energy · lots of pauses · topic: life |
| 5 | Sleep With Me | 6:20 | 0.756 | 0.86 / 0.67 / 0.72 | low energy · medium voices · slow pace · topic: life |

## kids story with funny voices
parsed (llm): vibe_text='Playful, whimsical narration using exaggerated, varied character voices; bright, upbeat tone with giggles and cartoonish sound effects; warm inviting storyteller voice alternating with high-pitched and gruff comedic voices.' targets={'energy': 'mid', 'expressiveness': 'high', 'pace_wpm': 'mid', 'laughter_score': 'high', 'music_score': 'mid'} topic='kids story' avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Circle Round | 2:20 | 0.899 | 0.97 / 0.83 / 0.89 | medium energy · expressive voices · lots of laughter · topic: kids story |
| 2 | Circle Round | 9:00 | 0.876 | 1.00 / 0.83 / 0.71 | lots of laughter · medium energy · expressive voices · topic: kids story |
| 3 | Stories Podcast: A Bedtime Show  | 7:00 | 0.876 | 0.93 / 0.76 / 1.00 | medium pace · medium music · expressive voices · topic: kids story |
| 4 | Stories Podcast: A Bedtime Show  | 4:40 | 0.872 | 0.86 / 0.88 / 0.88 | medium pace · expressive voices · medium music · topic: kids story |
| 5 | Nothing much happens: bedtime st | 3:40 | 0.844 | 0.87 / 0.83 / 0.81 | expressive voices · medium energy · lots of laughter · topic: kids story |

## relaxed chat between comedians, lots of laughs
parsed (llm): vibe_text='warm, laid-back conversational tone between two or more playful voices; casual banter, friendly teasing, frequent genuine laughter and chuckles; ambient room noise of a small studio; occasional overlapping talk, smiling vocal quality' targets={'energy': 'mid', 'expressiveness': 'high', 'pause_ratio': 'low', 'laughter_score': 'high'} topic=None avoid=['music_score:high', 'crowd_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Armchair Expert with Dax Shepard | 4:20 | 0.698 | 1.00 / 0.74 / 0.00 | few pauses · medium energy · expressive voices |
| 2 | Conan O’Brien Needs A Friend | 8:20 | 0.682 | 0.99 / 0.72 / 0.00 | expressive voices · few pauses · medium energy |
| 3 | Off Menu with Ed Gamble and Jame | 6:00 | 0.682 | 0.92 / 0.79 / 0.00 | few pauses · lots of laughter · expressive voices |
| 4 | SmartLess | 2:00 | 0.668 | 0.93 / 0.74 / 0.00 | expressive voices · medium energy · few pauses |
| 5 | Conan O’Brien Needs A Friend | 5:00 | 0.656 | 0.92 / 0.72 / 0.00 | few pauses · expressive voices · lots of laughter |

# More like this

## seed: Football Daily @ 6:40

| # | show | at | score | why |
|---|---|---|---|---|
| 1 | Football Daily | 9:20 | 0.789 | fast pace |
| 2 | The Totally Football Show with J | 2:00 | 0.773 | crowd noise · no music · lots of laughter |
| 3 | Football Daily | 3:20 | 0.761 | fast pace · lots of laughter · crowd noise |
| 4 | The Totally Football Show with J | 4:20 | 0.759 | no music · expressive voices |
| 5 | Men In Blazers | 5:00 | 0.756 | lots of laughter · crowd noise · high energy |

## seed: Get Sleepy: stories for sleep @ 5:20

| # | show | at | score | why |
|---|---|---|---|---|
| 1 | Get Sleepy: stories for sleep | 4:20 | 0.755 | no crowd · slow pace |
| 2 | Get Sleepy: stories for sleep | 4:20 | 0.728 | no crowd |
| 3 | Tara Brach | 3:20 | 0.708 | no crowd · lots of pauses · music |
| 4 | ASMR by GentleWhispering | 3:20 | 0.69 | lots of pauses · no crowd · flat delivery |
| 5 | ASMR by GentleWhispering | 2:40 | 0.689 | lots of pauses · no crowd · slow pace |

## seed: Fresh Air @ 6:20

| # | show | at | score | why |
|---|---|---|---|---|
| 1 | The Daily | 2:00 | 0.697 | no music · few pauses |
| 2 | Up First from NPR | 9:00 | 0.657 | no laughter |
| 3 | All Songs Considered | 6:20 | 0.652 | no music |
| 4 | Up First from NPR | 5:20 | 0.645 | expressive voices |
| 5 | Circle Round | 9:40 | 0.641 | expressive voices · no crowd |

LLM spend log: {"2026-10-20": {"usd": 0.006339, "calls": 22}, "2026-10-21": {"usd": 0.000289, "calls": 1}}