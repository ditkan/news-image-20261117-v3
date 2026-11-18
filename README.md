# news-image-20261117-v3

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/ditkan/news-image-20261117-v3/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/ditkan/news-image-20261117-v3/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

**"The World in a Day"** — Tuesday 17 November 2026's world news on one clean broadsheet page: **26 complete stories across 6 continents**, drawn entirely by program.

A design of our own: an airy, large-type front page rather than a dense wall of text. One big lead (the Kerch Bridge strike), three secondary features set larger (the COP31 draft, the Shenzhen trilateral, America losing its measles-free status), a dot-grid world map with markers for the mapped stories, a "Day in Numbers" box, and a numbered digest grouped by continent — Europe 7 · Asia 7 · North America 4 · Africa 4 · South America 2 · Oceania 2 — over a wire ticker and a full sources line. Every story is a headline plus a complete summary with the day's key facts and figures; the reporting behind each numbered story is listed in `sources.txt`. The layout is measured and balanced by the program itself: stories are never set smaller than the page's floor sizes — if a draft overflows, the program drops the lowest-priority stories instead of shrinking the type.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

Writes `entry.png` (1024×1024 PNG) to the output directory. The program renders at 2048×2048 and downscales; it is deterministic — the same bytes on every run — and needs no network and no inputs. Requires Python 3 with Pillow and the Noto Serif / Noto Sans fonts.

## Layout of the repo

- `main.py` — entry point (program/v1 contract)
- `render.py` — the whole newspaper: story data, dot-grid map, measured layout
- `entry.png` — the rendered page, as submitted
- `sources.txt` — the reporting behind every story on the page
