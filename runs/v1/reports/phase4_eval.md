# Phase 4: sanity evaluation (weak labels, no labelling)

Weights fixed at 0.4/0.4/0.2 from config; nothing was tuned on these queries.

## 1+3. Category check: share of top 10 from the expected iTunes category

| half | query | expected | random | embedding only | features only | hybrid |
|---|---|---|---|---|---|---|
| A | calm guided relaxation | Health & Fitness | 15% | 80% | 80% | 90% |
| A | comedians joking around | Comedy | 15% | 90% | 70% | 90% |
| A | crime story narration | True Crime | 10% | 30% | 10% | 50% |
| A | sports talk | Sports | 10% | 60% | 10% | 80% |
| B | news headlines briefing | News | 15% | 90% | 30% | 80% |
| B | a bedtime story for children | Kids & Family | 8% | 20% | 0% | 0% |
| B | music with singing and instruments | Music | 10% | 20% | 20% | 50% |
| B | soft whispering to help you sleep | Health & Fitness | 15% | 90% | 20% | 100% |
| A | **mean** | | 13% | 65% | 43% | 77% |
| B | **mean** | | 12% | 55% | 18% | 57% |

## 2+3. More-like-this: share of top 10 from the seed's own show (50 random seeds, neighbours excluded)

| random | embedding only | features only | hybrid |
|---|---|---|---|
| 2% | 41% | 19% | 43% |