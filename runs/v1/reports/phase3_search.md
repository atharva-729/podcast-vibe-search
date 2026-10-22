# Phase 3: demo queries (top 5)

## two friends laughing about football, late-night energy
parsed (llm): vibe_text='two close friends bantering and laughing together with a warm, late-night, high-energy tone; voices are animated, slightly husky from late hour, frequent overlapping chuckles and informal conversational rhythm, occasional exclamations and playful teasing; background is intimate rather than noisy.' targets={'energy': 'high', 'expressiveness': 'high', 'pace_wpm': 'mid', 'laughter_score': 'high'} topic='football' avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | The Bill Simmons Podcast | 6:20 | 0.8 | 0.82 / 0.80 / 0.74 | high energy · expressive voices · lots of laughter · topic: football |
| 2 | Armchair Expert with Dax Shepard | 4:20 | 0.792 | 1.00 / 0.80 / 0.36 | medium pace · expressive voices · lots of laughter |
| 3 | The Bill Simmons Podcast | 5:40 | 0.778 | 0.70 / 0.87 / 0.74 | medium pace · lots of laughter · high energy · topic: football |
| 4 | The Totally Football Show with J | 5:40 | 0.769 | 0.65 / 0.88 / 0.78 | expressive voices · high energy · lots of laughter · topic: football |
| 5 | Conan O’Brien Needs A Friend | 2:40 | 0.763 | 0.83 / 0.87 / 0.42 | expressive voices · high energy · medium pace |

## calm, slow, one voice, like a bedtime story
parsed (llm): vibe_text='single gentle voice, whispery/soft timbre, warm and soothing, minimal background sound, intimate lullaby-like ambience' targets={'energy': 'low', 'expressiveness': 'mid', 'pace_wpm': 'low', 'pause_ratio': 'high', 'music_score': 'low'} topic=None avoid=['music_score:high', 'energy:high', 'crowd_score:high', 'laughter_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Get Sleepy: stories for sleep | 5:20 | 0.617 | 1.00 / 0.54 / 0.00 | slow pace · lots of pauses |
| 2 | Nothing much happens: bedtime st | 6:20 | 0.568 | 0.77 / 0.65 / 0.00 | slow pace · lots of pauses |
| 3 | Get Sleepy: stories for sleep | 4:40 | 0.544 | 0.78 / 0.58 / 0.00 | lots of pauses · slow pace |
| 4 | Nothing much happens: bedtime st | 4:20 | 0.542 | 0.70 / 0.66 / 0.00 | slow pace · low energy · lots of pauses |
| 5 | ASMR by GentleWhispering | 3:20 | 0.539 | 0.64 / 0.71 / 0.00 | medium voices · slow pace · low energy |

## heated argument, people talking over each other
parsed (llm): vibe_text='confrontational, tense voices overlapping and interrupting each other; raised volume, sharp tone, quick exchanges, occasional shouting and breathy interjections' targets={'energy': 'high', 'expressiveness': 'high', 'pause_ratio': 'low', 'laughter_score': 'low', 'crowd_score': 'high'} topic=None avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Slow Radio | 4:20 | 0.644 | 1.00 / 0.61 / 0.00 | crowd noise · few pauses |
| 2 | Armchair Expert with Dax Shepard | 7:20 | 0.629 | 0.82 / 0.75 / 0.00 | few pauses · expressive voices · crowd noise |
| 3 | Crime Junkie | 3:00 | 0.62 | 0.79 / 0.76 / 0.00 | high energy · no laughter · expressive voices |
| 4 | The Journal. | 7:00 | 0.613 | 0.66 / 0.87 / 0.00 | expressive voices · high energy · no laughter |
| 5 | Armchair Expert with Dax Shepard | 3:40 | 0.605 | 0.70 / 0.81 / 0.00 | crowd noise · few pauses · expressive voices |

## soft whispering, very quiet
parsed (llm): vibe_text='very soft whispering, intimate and hushed voice, breathy tones, minimal background noise' targets={'energy': 'low', 'expressiveness': 'mid', 'pause_ratio': 'high'} topic=None avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | ASMR by GentleWhispering | 7:40 | 0.689 | 0.90 / 0.82 / 0.00 | medium voices · low energy |
| 2 | ASMR by GentleWhispering | 3:00 | 0.68 | 0.83 / 0.87 / 0.00 | medium voices · low energy · lots of pauses |
| 3 | Get Sleepy: stories for sleep | 5:20 | 0.673 | 1.00 / 0.68 / 0.00 | lots of pauses |
| 4 | Nothing much happens: bedtime st | 6:20 | 0.669 | 0.93 / 0.74 / 0.00 | lots of pauses |
| 5 | ASMR For Sleep And Relaxation | 4:00 | 0.669 | 0.90 / 0.78 / 0.00 | low energy · medium voices |

## excited fast talking about sports
parsed (llm): vibe_text='energetic, enthusiastic voices with noticeable pitch variation and quick delivery; occasional short laughs or exclamations; minimal background noise' targets={'energy': 'high', 'expressiveness': 'high', 'pace_wpm': 'high', 'laughter_score': 'mid'} topic='sports' avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | The Bill Simmons Podcast | 6:00 | 0.828 | 0.85 / 0.80 / 0.84 | fast pace · high energy · medium laughter · topic: sports |
| 2 | The Bill Simmons Podcast | 5:00 | 0.819 | 0.75 / 0.82 / 0.96 | fast pace · expressive voices · medium laughter · topic: sports |
| 3 | WTF with Marc Maron Podcast | 4:20 | 0.786 | 0.83 / 0.81 / 0.64 | expressive voices · fast pace · high energy · topic: sports |
| 4 | The Totally Football Show with J | 5:00 | 0.773 | 0.72 / 0.81 / 0.81 | high energy · expressive voices · medium laughter · topic: sports |
| 5 | Men In Blazers | 6:00 | 0.762 | 0.89 / 0.75 / 0.52 | expressive voices · high energy |

## serious news voice reading the headlines
parsed (llm): vibe_text='Calm, authoritative, and neutral news anchor voice with clear diction, steady pacing, minimal emotive inflection, low background ambience.' targets={'energy': 'mid', 'expressiveness': 'low', 'pace_wpm': 'mid', 'pause_ratio': 'mid', 'music_score': 'low', 'laughter_score': 'low', 'crowd_score': 'low'} topic='news' avoid=['music_score:high', 'laughter_score:high', 'expressiveness:high', 'crowd_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Up First from NPR | 5:40 | 0.801 | 0.96 / 0.56 / 0.95 | no laughter · medium pauses · no crowd · topic: news |
| 2 | Criminal | 5:20 | 0.792 | 0.86 / 0.72 / 0.81 | medium pace · no laughter · flat delivery · topic: news |
| 3 | Global News Podcast | 5:40 | 0.784 | 0.88 / 0.67 / 0.82 | medium pace · medium energy · no laughter · topic: news |
| 4 | Up First from NPR | 2:00 | 0.78 | 0.80 / 0.68 / 0.94 | flat delivery · medium pauses · no laughter · topic: news |
| 5 | Global News Podcast | 3:20 | 0.776 | 1.00 / 0.56 / 0.76 | no laughter · medium pauses · medium energy · topic: news |

## dramatic storytelling about a murder
parsed (llm): vibe_text='deep, resonant voice with deliberate pacing and strong emotional inflection; tense, slow-building atmosphere with sparse ambient textures and dark, cinematic undertone; occasional breaths and soft pauses to heighten suspense' targets={'energy': 'mid', 'expressiveness': 'high', 'pace_wpm': 'low', 'pause_ratio': 'high', 'music_score': 'mid'} topic='murder' avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Nothing much happens: bedtime st | 7:00 | 0.926 | 1.00 / 0.93 / 0.77 | medium music · slow pace · medium energy · topic: murder |
| 2 | Crime Junkie | 7:20 | 0.861 | 0.93 / 0.80 / 0.86 | lots of pauses · medium energy · expressive voices · topic: murder |
| 3 | Circle Round | 4:20 | 0.837 | 0.85 / 0.86 / 0.77 | medium music · lots of pauses · slow pace · topic: murder |
| 4 | Circle Round | 3:40 | 0.823 | 0.81 / 0.92 / 0.65 | medium music · expressive voices · slow pace · topic: murder |
| 5 | Nothing much happens: bedtime st | 6:20 | 0.807 | 0.86 / 0.94 / 0.44 | medium energy · expressive voices · slow pace |

## rain and nature sounds, no talking
parsed (llm): vibe_text='gentle ambient rain and natural outdoor sounds, no human voices, calm and immersive, soft water and rustling leaves' targets={'energy': 'low', 'expressiveness': 'low', 'pause_ratio': 'high', 'music_score': 'low', 'crowd_score': 'low', 'laughter_score': 'low'} topic=None avoid=['expressiveness:high', 'music_score:high', 'laughter_score:high', 'crowd_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Get Sleepy: stories for sleep | 6:00 | 0.667 | 0.97 / 0.70 / 0.00 | lots of pauses · no laughter · flat delivery |
| 2 | ASMR For Sleep And Relaxation | 6:00 | 0.618 | 1.00 / 0.55 / 0.00 | flat delivery · no crowd · low energy |
| 3 | ASMR by GentleWhispering | 6:40 | 0.611 | 0.95 / 0.57 / 0.00 | lots of pauses · low energy · no crowd |
| 4 | ASMR For Sleep And Relaxation | 3:40 | 0.608 | 0.96 / 0.56 / 0.00 | flat delivery · no crowd · low energy |
| 5 | ASMR by GentleWhispering | 5:20 | 0.606 | 0.92 / 0.59 / 0.00 | flat delivery · no crowd · lots of pauses |

## upbeat music and singing
parsed (llm): vibe_text='bright, energetic, rhythmic with melodic vocals and prominent upbeat instrumentation' targets={'energy': 'high', 'expressiveness': 'high', 'music_score': 'high', 'laughter_score': 'low'} topic=None avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | The Story Seeds Podcast | 5:40 | 0.678 | 0.87 / 0.83 / 0.00 | music · expressive voices · no laughter |
| 2 | Switched on Pop | 6:00 | 0.641 | 0.76 / 0.84 / 0.00 | music · no laughter · expressive voices |
| 3 | ASMR by GentleWhispering | 5:40 | 0.639 | 0.74 / 0.86 / 0.00 | no laughter · music · expressive voices |
| 4 | Fresh Air | 6:40 | 0.636 | 0.94 / 0.65 / 0.00 | expressive voices · music |
| 5 | Switched on Pop | 3:20 | 0.629 | 0.69 / 0.88 / 0.00 | high energy · expressive voices · music |

## thoughtful slow interview about life
parsed (llm): vibe_text='calm, intimate conversation with warm, reflective voices; gentle low background hum or soft ambient pad; minimal production so speech feels close and personal' targets={'energy': 'low', 'expressiveness': 'mid', 'pace_wpm': 'low', 'pause_ratio': 'high', 'music_score': 'low'} topic='life' avoid=['music_score:high', 'energy:high', 'laughter_score:high', 'crowd_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Tara Brach | 7:00 | 0.78 | 0.85 / 0.74 / 0.71 | slow pace · no music · low energy · topic: life |
| 2 | Sleep With Me | 6:20 | 0.77 | 0.91 / 0.68 / 0.67 | low energy · medium voices · no music · topic: life |
| 3 | Tara Brach | 2:40 | 0.765 | 0.83 / 0.71 / 0.74 | slow pace · low energy · lots of pauses · topic: life |
| 4 | The Story Seeds Podcast | 7:40 | 0.744 | 0.85 / 0.70 / 0.62 | no music · medium voices · lots of pauses · topic: life |
| 5 | Sleep With Me | 7:00 | 0.72 | 0.85 / 0.66 / 0.57 | medium voices · no music |

## kids story with funny voices
parsed (llm): vibe_text='Playful, whimsical narration using exaggerated, varied character voices; bright, upbeat tone with giggles and cartoonish sound effects; warm inviting storyteller voice alternating with high-pitched and gruff comedic voices.' targets={'energy': 'mid', 'expressiveness': 'high', 'pace_wpm': 'mid', 'laughter_score': 'high', 'music_score': 'mid'} topic='kids story' avoid=[]

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Circle Round | 2:20 | 0.913 | 1.00 / 0.83 / 0.90 | medium energy · expressive voices · lots of laughter · topic: kids story |
| 2 | Stories Podcast: A Bedtime Show  | 7:00 | 0.881 | 0.96 / 0.75 / 1.00 | medium pace · medium music · expressive voices · topic: kids story |
| 3 | Stories Podcast: A Bedtime Show  | 4:40 | 0.874 | 0.89 / 0.86 / 0.87 | expressive voices · medium pace · medium music · topic: kids story |
| 4 | Circle Round | 7:00 | 0.859 | 0.97 / 0.75 / 0.86 | expressive voices · medium music · topic: kids story |
| 5 | The Story Seeds Podcast | 5:40 | 0.818 | 0.99 / 0.78 / 0.55 | medium energy · expressive voices · medium music |

## relaxed chat between comedians, lots of laughs
parsed (llm): vibe_text='warm, laid-back conversational tone between two or more playful voices; casual banter, friendly teasing, frequent genuine laughter and chuckles; ambient room noise of a small studio; occasional overlapping talk, smiling vocal quality' targets={'energy': 'mid', 'expressiveness': 'high', 'pause_ratio': 'low', 'laughter_score': 'high'} topic=None avoid=['music_score:high', 'crowd_score:high']

| # | show | at | score | vibe / feature / topic | why |
|---|---|---|---|---|---|
| 1 | Armchair Expert with Dax Shepard | 4:20 | 0.693 | 1.00 / 0.73 / 0.00 | few pauses · medium energy · expressive voices |
| 2 | Off Menu with Ed Gamble and Jame | 6:00 | 0.67 | 0.91 / 0.76 / 0.00 | few pauses · lots of laughter · expressive voices |
| 3 | SmartLess | 2:00 | 0.666 | 0.92 / 0.74 / 0.00 | medium energy · expressive voices · few pauses |
| 4 | Conan O’Brien Needs A Friend | 5:00 | 0.646 | 0.91 / 0.70 / 0.00 | few pauses · expressive voices · lots of laughter |
| 5 | Armchair Expert with Dax Shepard | 2:00 | 0.639 | 0.85 / 0.75 / 0.00 | few pauses · lots of laughter · medium energy |

# More like this

## seed: The Bill Simmons Podcast @ 6:20

| # | show | at | score | why |
|---|---|---|---|---|
| 1 | The Bill Simmons Podcast | 3:20 | 0.729 | expressive voices · crowd noise · fast pace |
| 2 | The Totally Football Show with J | 2:00 | 0.714 | crowd noise · lots of laughter · no music |
| 3 | Conan O’Brien Needs A Friend | 3:40 | 0.705 | no music · high energy · lots of laughter |
| 4 | The Totally Football Show with J | 7:20 | 0.705 | fast pace · lots of laughter · crowd noise |
| 5 | Conan O’Brien Needs A Friend | 2:40 | 0.702 | lots of laughter · no music · crowd noise |

## seed: Get Sleepy: stories for sleep @ 5:20

| # | show | at | score | why |
|---|---|---|---|---|
| 1 | Get Sleepy: stories for sleep | 4:20 | 0.749 | flat delivery · no crowd · slow pace |
| 2 | Get Sleepy: stories for sleep | 7:00 | 0.678 | no crowd · flat delivery |
| 3 | Nothing much happens: bedtime st | 6:20 | 0.665 | lots of pauses · no crowd · no laughter |
| 4 | ASMR by GentleWhispering | 7:40 | 0.616 | no laughter · no crowd · slow pace |
| 5 | ASMR by GentleWhispering | 3:40 | 0.612 | flat delivery · slow pace · no crowd |

## seed: Slow Radio @ 4:20

| # | show | at | score | why |
|---|---|---|---|---|
| 1 | Slow Radio | 5:00 | 0.843 | few pauses · low energy · slow pace |
| 2 | Slow Radio | 3:00 | 0.753 | few pauses · slow pace · low energy |
| 3 | ASMR For Sleep And Relaxation | 5:00 | 0.599 | low energy · no crowd · slow pace |
| 4 | ASMR For Sleep And Relaxation | 2:40 | 0.587 | low energy · few pauses · slow pace |
| 5 | Relaxing Nature Sounds | 4:40 | 0.578 | few pauses · slow pace · expressive voices |

LLM spend log: {"2026-10-20": {"usd": 0.006339, "calls": 22}}