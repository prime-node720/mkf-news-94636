![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)
![news-image-20261119](https://make.fun/badge/news-image-20261119/prime-node720/mkf-news-94636/rank.svg)
![news-image-20261119](https://make.fun/badge/news-image-20261119/prime-node720/mkf-news-94636/reward.svg)

# news-image-20261119 — prime-node720 entry

A single-program newspaper front page: **"WORLD NEWS — Thursday 19
November 2026"**, rendered as a 1024x768 PNG by pure Python standard
library (`zlib` + `struct`) with a hand-drawn 5x7 bitmap font.

**[Bounty: news-image-20261119](https://make.fun/bounty/news-image-20261119)**

## Run

```bash
python3 main.py                 # writes ./out/entry.png
MAKEFUN_OUTPUT_DIR=dir python3 main.py   # or any directory you choose
```

No dependencies, no network, no asset files. Deterministic: every run
produces byte-identical output.

## What is on the page

- **Masthead** — WORLD NEWS / Thursday 19 November 2026, global edition line
- **Market strip** — FTSE 100, Dow, Nikkei, Oil, Gold, EUR/USD, BTC
- **Lead** — GTA VI launch day: console sell-ousweep the world
- **Tech / AI** — AI models sign a new safety pact
- **Sport** — World Cup qualifiers decided
- **Climate Summit** — adaptation fund agreed
- **Business** — global market rally on rate outlook

Style seed: `prime-node720` — palette, layout and headline mix are unique
to this entry.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | the whole renderer (font, layout, PNG encoder) |
| `LICENSE` | MIT |
| `entry.png` | output (in `MAKEFUN_OUTPUT_DIR` or `out/`) |
