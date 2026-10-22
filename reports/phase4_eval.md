# Phase 4: sanity evaluation (weak labels, no labelling)

Weights fixed at 0.4/0.4/0.2 from config; nothing was tuned on these queries.

## 1+3. Category check: share of top 10 from the expected iTunes category

| half | query | expected | random | embedding only | features only | hybrid |
|---|---|---|---|---|---|---|
| A | calm guided relaxation | Health & Fitness | 15% | 70% | 60% | 70% |
| A | comedians joking around | Comedy | 15% | 90% | 50% | 90% |
| A | crime story narration | True Crime | 10% | 30% | 10% | 70% |
| A | sports talk | Sports | 10% | 60% | 10% | 100% |
| B | news headlines briefing | News | 15% | 100% | 50% | 80% |
| B | a bedtime story for children | Kids & Family | 8% | 0% | 0% | 0% |
| B | music with singing and instruments | Music | 10% | 40% | 30% | 60% |
| B | soft whispering to help you sleep | Health & Fitness | 15% | 90% | 0% | 100% |
| A | **mean** | | 13% | 62% | 33% | 82% |
| B | **mean** | | 12% | 57% | 20% | 60% |

## 2+3. More-like-this: share of top 10 from the seed's own show (50 random seeds, neighbours excluded)

| random | embedding only | features only | hybrid |
|---|---|---|---|
| 2% | 54% | 23% | 58% |