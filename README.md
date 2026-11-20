# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/WV629/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/WV629/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A one-page newspaper front page summing up the world news of Friday 20 November 2026 in a single image — 36 stories in all: a headline stat strip, 13 drawn feature stories (Cyclone Akvan, the Kyiv missile strikes, COP31's final-day deadlock, Asia's worst week since 2020, BepiColombo reaching Mercury, and more), 23 further briefs, a world map with numbered pins, and a DATE CHECK box that names the big Thursday 19 November stories and keeps them out of the Friday paper.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image itself is drawn in code by `generate.py` (Pillow, no network, deterministic) and committed as `entry.png`; `main.py` copies it to the harness output directory.

---

<sub>Entered on [make.fun](https://make.fun/?ref=wkn1wnrf&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
