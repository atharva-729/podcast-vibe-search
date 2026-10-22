# Phase 4: sanity evaluation (weak labels, no labelling)

Weights fixed at 0.4/0.4/0.2 from config; nothing was tuned on these queries.

## 1+3. Category check: share of top 10 from the expected iTunes category

| half | query | expected | random | embedding only | features only | hybrid |
|---|---|---|---|---|---|---|
| A | calm guided relaxation | Health & Fitness | 15% | 70% | 80% | 80% |
| A | comedians joking around | Comedy | 15% | 40% | 70% | 70% |
| A | crime story narration | True Crime | 10% | 0% | 10% | 20% |
| A | sports talk | Sports | 10% | 30% | 10% | 60% |
| B | news headlines briefing | News | 15% | 40% | 30% | 60% |
| B | a bedtime story for children | Kids & Family | 8% | 10% | 0% | 10% |
| B | music with singing and instruments | Music | 10% | 30% | 20% | 30% |
| B | soft whispering to help you sleep | Health & Fitness | 15% | 90% | 20% | 100% |
| A | **mean** | | 13% | 35% | 43% | 57% |
| B | **mean** | | 12% | 43% | 18% | 50% |

## 2+3. More-like-this: share of top 10 from the seed's own show (50 random seeds, neighbours excluded)

| random | embedding only | features only | hybrid |
|---|---|---|---|
| 2% | 41% | 19% | 43% |