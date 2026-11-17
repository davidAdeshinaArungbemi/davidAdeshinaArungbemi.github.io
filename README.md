# davidadeshinaarungbemi.github.io

Personal site of David Adeshina Arungbemi (also writes as Suzume 雀). GitHub Pages publishes it from `main`.

## How the pages are made

The public pages are built by the scripts in `_tools/` (folders starting with `_` are never published). Run them from the repo root, in this order:

1. `python3 _tools/build_cards.py`: the projects (`PROJECTS`, `TAGS`, and `HOME` for the homepage).
2. `python3 _tools/build_gallery.py`: Worlds (`images.html`) from `GROUPS`, plus the homepage's Worlds selection (`SHOWCASE`) and the clips its screen plays (`CLIPS`).
3. `/opt/miniconda3/bin/python3 _tools/build_blog.py`: the article pages from `_writing/<slug>.html`, the Articles page and `sitemap.xml`. Add `--import` to copy new Medium posts in first.
4. `/opt/miniconda3/bin/python3 _tools/build_topics.py`: the four topic pages and the projects page.

Every script writes the colour palettes (`assets/design/moods.css`, read from the pictures; the first run takes a couple of minutes, later runs reuse the readings) and ends by rebuilding the homepage (`_tools/build_home.py`, which also holds the homepage's own words). So after an edit, run the steps from the one you touched to the end. Steps 3 and 4 need bs4, which the miniconda Python has; steps 1 and 2 also run with the system Python.

Two things to know when adding work:

- A new article shows under a research topic only once it is listed in `TOPICS` in `_tools/build_topics.py` (a new topic also needs a colour in `TOPIC_HUES` in `_tools/design.py`).
- On the homepage, an article whose `kind` contains "experiment" goes under Experiments; every other kind goes under Essays. `home: true` puts it in the homepage's own selection.

Then `python3 _tools/check_site.py` checks every page: structure, names, links and anchors, and a comparison with `main` (the text, the alt texts, and the title, description, link-preview and JSON-LD lines).

Written by hand: `cv.html` (print → save as PDF) and `404.html`.

## Files

- `_tools/design.py`: the look and the furniture every page shares (header, footer, cards, the topic bar, the clip showcase); `_tools/moods.py` turns each picture into a palette checked for AA contrast.
- `assets/design/`: `style.css`, the generated `moods.css`, and the scripts (`scheme.js`, `mood.js`, `showcase.js`, `page.js`).
- `assets/site.css`, `assets/site.js`, `assets/theme.js`: the earlier look, still used by the unlisted pages under `for/`. Leave these three as they are.
- `assets/fonts/`: self-hosted fonts; nothing loads from other sites.
- `Notebooks/`, `docs/`: PDFs linked from the site.
