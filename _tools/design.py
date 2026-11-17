"""The site's look and the furniture every page shares. Chosen by David on 17 Nov 2026 ("D" in the prototypes
that are kept in _directions/).

The design: his work seen through his four research topics (colour fields, a topic bar that recolours the page
and brings a topic's work forward, cards with the picture on top), inside a dark room whose light follows what is
shown, with a lit screen for the clips at the top of the homepage. Square blocks with colour bars; only the screen
is rounded.

Files:
  assets/design/style.css     the look (written by hand)
  assets/design/moods.css     one palette per picture, each checked for AA contrast (write_moods() writes it)
  assets/design/scheme.js     light or dark, settled before the page paints
  assets/design/mood.js       which palette the page wears: what is pointed at, the section in view, the clip
  assets/design/showcase.js   the homepage clips
  assets/design/page.js       the topic bar, filters, cards that colour themselves, the viewer, videos in view
The older assets/site.css, site.js and theme.js stay as they are for the unlisted pages under for/.

Every build script ends with design.finish(), which rebuilds the homepage and moods.css, so the documented build order
(build_cards, build_gallery, build_blog, build_topics) always leaves the whole site current.
"""
import html, re
from functools import lru_cache
from pathlib import Path
from PIL import Image

import moods

SITE = "https://davidadeshinaarungbemi.github.io"
MEDIUM = "https://suzume1.medium.com/"
FEED = "https://medium.com/feed/@suzume1"
GITHUB_SUZUME, GITHUB_DAVID = "https://github.com/suzume-hue", "https://github.com/davidAdeshinaArungbemi"
DESIGN = Path("assets/design")

esc = lambda s: html.escape(s, quote=False)
attr = lambda s: html.escape(s, quote=True)

def absolute(u):
    """Site-absolute form of a link or image address written relative to the site root."""
    return u if u.startswith(("http://", "https://", "/", "#", "mailto:")) else "/" + u

# ---------------------------------------------------------------- words every page shares (his own)

# the second half of the homepage's opening line; the name sits beside it in the header
ALSO = 'also writes as <a class="seal-inline" href="#suzume"><img src="/assets/img/seal.png" alt="" width="14" height="14"> Suzume</a>'
FOOT = '© 2026 David Adeshina Arungbemi. Also <img class="seal-tiny" src="/assets/img/seal.png" alt="" width="12" height="12"> Suzume.'

NAV = [("Research", "/#research"), ("Publications", "/#publications"), ("Articles", "/articles/"),
       ("Projects", "/projects/"), ("Worlds", "/images.html"), ("CV", "/cv.html"), ("Contact", "/#contact")]
HOME_NAV = [("Research", "#research"), ("Publications", "#publications"), ("Articles", "#articles"),
            ("Projects", "#projects"), ("Worlds", "#worlds"), ("CV", "/cv.html"), ("Contact", "#contact")]

ICON = {
    "prev": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "next": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "toggle": '<svg class="i-pause" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M8 5v14M16 5v14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>'
              '<svg class="i-play" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg>',
    "scheme": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3.8a8.2 8.2 0 0 0 0 16.4z" fill="currentColor"/></svg>',
}

# ---------------------------------------------------------------- pictures

@lru_cache(maxsize=None)
def size(src):
    with Image.open(src.lstrip("/")) as im:
        return im.size

def smaller(src):
    """The 800px copy of an image, if there is one."""
    p = Path(src.lstrip("/"))
    s = p.with_name(p.stem + "-800" + p.suffix)
    return "/" + str(s) if s.exists() else src

def mood_name(src):
    """The name of the palette a picture gives (the same for all its sizes)."""
    p = Path(src.lstrip("/"))
    stem = re.sub(r"-(800|1200|1600)$", "", p.stem)
    parts = [x for x in p.parts[:-1] if x != "assets"]
    return re.sub(r"[^a-z0-9-]+", "-", "-".join(parts + [stem]).lower()).strip("-")

TOPIC_HUES = {"stories-and-ai": 52, "aesthetics": 352, "visualisation": 238, "minds": 298}

# ---------------------------------------------------------------- the page shell

def keep_meta(page_html):
    """The title, description, robots, canonical, Open Graph, Twitter and JSON-LD lines of an existing page,
    exactly as they are, so a rebuild never changes what search engines and link previews see."""
    head = re.search(r"<head>(.*?)</head>", page_html, re.S).group(1)
    keep = []
    for line in head.strip().splitlines():
        s = line.strip()
        if (s.startswith("<title>") or s.startswith('<script type="application/ld+json">')
                or re.match(r'<meta (name="(description|robots|twitter:[a-z]+)"|property="(og|article):[a-z_:]+")', s)
                or s.startswith('<link rel="canonical"')):
            keep.append(s)
    return "\n".join(keep)

def meta(title, description, url, image, og_type="website", published=None, og_description=None, extra=""):
    """The meta lines for a generated page (the same set the earlier build wrote)."""
    article = ""
    if og_type == "article" and published:
        article = (f'\n<meta property="article:published_time" content="{published}">'
                   '\n<meta property="article:author" content="David Adeshina Arungbemi">')
    return (f"<title>{esc(title)}</title>\n"
            f'<meta name="description" content="{attr(description)}">\n'
            f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="{og_type}">\n'
            f'<meta property="og:title" content="{attr(title)}">\n'
            f'<meta property="og:description" content="{attr(og_description or description)}">\n'
            f'<meta property="og:image" content="{SITE}{image}">\n'
            f'<meta property="og:url" content="{url}">{article}\n'
            f'<meta name="twitter:card" content="summary_large_image">{extra}')

def head(meta_lines, mood="default", rss=False):
    feed = f'\n<link rel="alternate" type="application/rss+xml" title="Suzume on Medium" href="{FEED}">' if rss else ""
    return f"""<!DOCTYPE html>
<html lang="en" data-default-scheme="dark" data-mood="{mood}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{meta_lines}
<meta name="theme-color" content="#16181B" data-follow>
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/seal-32.png">
<link rel="icon" type="image/png" sizes="64x64" href="/assets/img/seal-64.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/img/seal-180.png">{feed}
<link rel="stylesheet" href="/assets/design/style.css">
<link rel="stylesheet" href="/assets/design/moods.css">
<script src="/assets/design/scheme.js"></script>
<script src="/assets/design/mood.js" defer></script>
<script src="/assets/design/showcase.js" defer></script>
<script src="/assets/design/page.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="glow" aria-hidden="true"></div>
"""

def nav_links(home=False, current=None):
    return "".join(f'<a href="{u}"' + (' aria-current="page"' if t == current else "") + f">{t}</a>" for t, u in (HOME_NAV if home else NAV))

def header(home=False, current=None):
    also = ALSO if home else ALSO.replace('href="#suzume"', 'href="/#suzume"')
    return (f'<header class="site-head"><div class="wrap site-head-row">'
            f'<a class="site-name" href="{"#top" if home else "/"}">David Adeshina Arungbemi</a>'
            f'<span class="site-also">{also}</span>'
            f'<nav class="site-nav" aria-label="Sections">{nav_links(home, current)}</nav>'
            f'<button class="icon-btn" type="button" data-scheme-toggle aria-label="Switch between light and dark">{ICON["scheme"]}</button>'
            f'</div></header>')

def footer(home=False):
    back = "" if home else ' <a href="/">Back to the site →</a>'
    return (f'<footer class="site-foot"><div class="wrap"><nav class="foot-nav" aria-label="Site">{nav_links(home)}</nav>'
            f'<p>{FOOT}{back}</p></div></footer>')

END = "</body>\n</html>\n"

def listed(page):
    """Lists styled without bullets lose their list role in Safari; say it outright."""
    for tag in ('<ol class="cards', '<ul class="topics"', '<ul class="contact-list"', '<ol class="showcase-picks"'):
        page = page.replace(tag, tag[:3] + ' role="list"' + tag[3:])
    return page

# ---------------------------------------------------------------- pieces

def tags_html(tags):
    return ('<ul class="tags">' + "".join(f"<li>{esc(t)}</li>" for t in tags) + "</ul>") if tags else ""

def card(link, img, kind, title, line, tags=(), extras=(), group=None, topics=(), home=None, level=3, ink=False):
    """One piece as a card: picture on top, label, title, one line, topic tags and extra links. The whole card is
    the link; pointed at or focused, it takes its own picture's colours (data-own)."""
    link, img = absolute(link), absolute(img)
    w, h = size(img)
    data = f' data-own="{mood_name(img)}"'
    if topics: data += f' data-topics="{" ".join(topics)}"'
    if group: data += f' data-kind="{group}"'
    if home is not None: data += " data-home" if home else " hidden"
    href = attr(link)
    extra = ('<p class="item-extra">' + "".join(f'<a href="{attr(absolute(u))}">{esc(t)}</a>' for t, u in extras) + "</p>") if extras else ""
    return (f'<li class="item"{data}>'
            f'<a class="item-thumb{" is-ink" if ink else ""}" href="{href}" tabindex="-1" aria-hidden="true"><img src="{attr(img)}" alt="" width="{w}" height="{h}" loading="lazy"></a>'
            f'<div class="item-text"><p class="item-kind">{esc(kind)}</p>'
            f'<h{level} class="item-title"><a href="{href}">{esc(title)}</a></h{level}>'
            f'<p class="item-line">{esc(line)}</p>{tags_html(tags)}{extra}</div></li>')

def feature(href, img, label, title, line, tags=(), topics=(), ink=False, home=True, level=3):
    """One article shown large: picture beside label, title, line and tags. home: True marks it part of the
    homepage selection, False hides it until a topic shows it, None leaves both out (a page without a topic bar)."""
    w, h = size(img)
    keep = "" if home is None else (" data-home" if home else " hidden")
    data = f' data-own="{mood_name(img)}"' + (f' data-topics="{" ".join(topics)}"' if topics else "") + keep
    return (f'<div class="feature"{data}>'
            f'<a class="feature-art{" is-ink" if ink else ""}" href="{attr(href)}" tabindex="-1" aria-hidden="true"><img src="{attr(img)}" alt="" width="{w}" height="{h}" loading="lazy"></a>'
            f'<div class="feature-text"><p class="item-kind">{esc(label)}</p>'
            f'<h{level} class="feature-title"><a href="{attr(href)}">{esc(title)}</a></h{level}>'
            f'<p class="feature-line">{esc(line)}</p>{tags_html(tags)}</div></div>')

def cards(items, cls=""):
    return f'<ol class="cards{cls}">' + "".join(items) + "</ol>"

def more(links):
    return '<p class="more">' + "".join(f'<a href="{attr(u)}">{t}</a>' for t, u in links) + "</p>"

def section(id_, title, inner, lensed=False, extra_head="", level=2):
    """One section: the heading and, under a topic, how much of it is showing."""
    ident = f' id="{id_}"' if id_ else ""
    if lensed:
        count = '<p class="lens-count" data-lens-count hidden></p>'
        empty = '<p class="lens-empty" data-lens-empty hidden>Nothing here for this topic.</p>'
        return (f'<section class="sec"{ident} data-lens-section><div class="wrap"><div class="sec-head"><h{level}>{title}</h{level}>{count}</div>'
                f'{extra_head}{empty}{inner}</div></section>')
    return f'<section class="sec"{ident}><div class="wrap"><div class="sec-head"><h{level}>{title}</h{level}></div>{extra_head}{inner}</div></section>'

def topic_tile(slug, title, line, count, lead_img):
    """A research topic as a field of its own colour: its lead picture, name, one line and how many pieces."""
    w, h = size(lead_img)
    m = f"topic-{slug}"
    return (f'<li class="topic" data-mood="{m}" data-topic="{slug}"><a href="/{slug}/">'
            f'<span class="topic-art"><img src="{attr(lead_img)}" alt="" width="{w}" height="{h}" loading="lazy"></span>'
            f'<span class="topic-title">{esc(title)}</span><span class="topic-line">{esc(line)}</span>'
            f'<span class="topic-count">{count} pieces →</span></a></li>')

def year(meta_text):
    m = re.search(r"(19|20)\d\d", meta_text)
    return f'<span class="world-year">{m.group(0)}</span>' if m else ""

def world(slug, title, meta_text, caption, alt, poster=None, topics=(), home=None):
    """A picture from Worlds as a card, linking to its place on the Worlds page; the whole picture shows on a mat."""
    img = poster or f"/assets/gallery/{slug}-800.jpg"
    w, h = size(img)
    data = f' data-own="{mood_name(img)}"' + (f' data-topics="{" ".join(topics)}"' if topics else "")
    if home is not None: data += " data-home" if home else " hidden"
    return (f'<figure class="world"{data}><a class="world-media" href="/images.html#{slug}">'
            f'<img src="{attr(img)}" alt="{attr(alt)}" width="{w}" height="{h}" loading="lazy"></a>'
            f'<figcaption><strong>{esc(title)}</strong><span class="world-desc">{esc(caption)}</span>{year(meta_text)}</figcaption></figure>')

def lens_bar(topics):
    """The topic bar: All, then the four topics; hidden until page.js runs. CV sits at its end."""
    buttons = ['<button class="lens-btn" type="button" aria-pressed="true" data-lens-pick="all">All</button>']
    for t in topics:
        m = f"topic-{t['slug']}"
        buttons.append(f'<button class="lens-btn" type="button" aria-pressed="false" data-lens-pick="{t["slug"]}" data-mood="{m}" data-peek="{m}" '
                       f'data-title="{attr(t["title"])}" data-href="/{t["slug"]}/">{esc(t["title"])}</button>')
    return ('<div class="lens" data-lens hidden><div class="wrap lens-inner">'
            f'<div class="lens-group" role="group" aria-label="Show work from"><span class="lens-label" aria-hidden="true">Show work from</span>{"".join(buttons)}</div>'
            '<p class="lens-go" data-lens-go hidden><a href="#" data-lens-link>Topic page →</a></p>'
            '<p class="lens-cv"><a href="/cv.html">CV</a></p>'
            '<p class="visually-hidden" role="status" data-lens-status></p></div></div>')

def filters(label, options, light=False):
    """Buttons that show one kind of piece at a time; hidden until page.js runs. options: (value, text, mood or None).
    With light=True, choosing one also lights the page with that mood."""
    out = []
    for i, (value, text, mood) in enumerate(options):
        m = f' data-mood-on="{mood}"' if mood else ""
        out.append(f'<button class="lens-btn filter-btn" type="button" data-filter="{value}" aria-pressed="{"true" if i == 0 else "false"}"{m}>{esc(text)}</button>')
    lit = " data-filters-light" if light else ""
    return f'<div class="filters" role="group" aria-label="{attr(label)}" data-filters{lit} hidden>{"".join(out)}</div>'

def showcase(clips):
    """The clip showcase: one clip at a time, moving on by itself. clips: dicts with slug, title, line, meta, src,
    poster, w, h, label (what the clip shows), seconds. Without the script: the first poster, its caption, and the
    picks as plain links to the pieces."""
    n = len(clips)
    slides, picks = [], []
    for i, cl in enumerate(clips):
        href = f"/images.html#{cl['slug']}"
        load = ' fetchpriority="high"' if i == 0 else ' loading="lazy"'
        slides.append(
            f'<figure class="showcase-slide" data-slide data-src="{attr(cl["src"])}" data-mood="{mood_name(cl["poster"])}" data-seconds="{cl["seconds"]}" '
            f'data-title="{attr(cl["title"])}"{"" if i == 0 else " hidden"}>'
            f'<div class="showcase-media"><img class="showcase-poster" src="{attr(cl["poster"])}" alt="{attr(cl["label"])}" width="{cl["w"]}" height="{cl["h"]}"{load}></div>'
            f'<figcaption class="showcase-caption" data-showcase-hold><span class="showcase-count" aria-hidden="true">{i + 1} / {n}</span>'
            f'<p class="showcase-title"><a href="{href}">{esc(cl["title"])}</a></p>'
            f'<p class="showcase-line">{esc(cl["line"])}</p><p class="showcase-meta">{esc(cl["meta"])}</p></figcaption></figure>')
        picks.append(
            f'<li><a href="{href}" data-showcase-pick aria-label="{attr(cl["title"])}">'
            f'<img class="pick-thumb" src="{attr(cl["poster"])}" alt="" width="{cl["w"]}" height="{cl["h"]}" loading="lazy">'
            f'<span class="pick-n" aria-hidden="true">{i + 1}</span><span class="pick-title">{esc(cl["title"])}</span>'
            f'<span class="pick-progress" aria-hidden="true"></span></a></li>')
    return (f'<section class="showcase" data-showcase data-colour="page" aria-label="Showcase">'
            f'<div class="showcase-stage" data-showcase-stage><canvas class="showcase-ambient" data-showcase-ambient width="24" height="15" aria-hidden="true"></canvas>{"".join(slides)}</div>'
            f'<div class="showcase-bar" data-showcase-hold><div class="showcase-controls">'
            f'<button type="button" data-showcase-prev aria-label="Previous clip">{ICON["prev"]}</button>'
            f'<button type="button" data-showcase-toggle data-state="paused" aria-label="Play the showcase">{ICON["toggle"]}</button>'
            f'<button type="button" data-showcase-next aria-label="Next clip">{ICON["next"]}</button></div>'
            f'<ol class="showcase-picks">{"".join(picks)}</ol></div>'
            f'<p class="visually-hidden" data-showcase-status aria-live="polite"></p></section>')

# ---------------------------------------------------------------- the palettes

def pictures():
    """Every picture a page can take its colours from, by palette name."""
    import build_blog, build_cards, build_gallery, build_home, build_topics
    pics = {}
    def add(src):
        src = absolute(src)
        pics.setdefault(mood_name(src), smaller(src))
    for p in build_cards.PROJECTS:
        add(p[1])
    for post in build_blog.load_all():
        add(post["cover"])
        if post.get("art"): add(post["art"])
        for src in re.findall(r'<img[^>]*?\ssrc="(/[^"]+)"', post["body"]):
            add(src)
    for _, _, _, items in build_gallery.GROUPS:
        for it in items:
            add(build_gallery.VIDEOS[it[0]][1] if it[0] in build_gallery.VIDEOS else f"/assets/gallery/{it[0]}-800.jpg")
    for p in build_topics.PUBS.values():
        add(p[1])
    for p in build_home.PUBS:
        add(p["img"])
    add(build_home.ART["src"])
    return pics

CACHE = Path("_tools/__pycache__/moods.json")    # gitignored (__pycache__/): reading a picture's colours is slow

def analysed_pictures():
    """name -> analysis for every picture, reusing earlier readings of files that haven't changed."""
    import json, os
    try:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    out, fresh = {}, {}
    for name, src in sorted(pictures().items()):
        path = src.lstrip("/")
        st = os.stat(path)
        key = f"{path}|{st.st_size}|{int(st.st_mtime)}"
        out[name] = cache.get(key) or moods.analyse(path)
        fresh[key] = out[name]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(fresh), encoding="utf-8")
    return out

def write_moods():
    """assets/design/moods.css: the default palette, the four topics, and one palette per picture, in the dark
    scheme the site opens in and the light one the toggle gives. Every text pair is checked for AA."""
    analysed = {"default": moods.fixed(250, 0.0)}
    for slug, hue in TOPIC_HUES.items():
        analysed[f"topic-{slug}"] = moods.fixed(hue, 0.85, (hue + 32) % 360)
    analysed.update(analysed_pictures())

    unused = {"accent-2", "glow-2"}                     # computed and checked, but style.css never uses them

    def block(a, scheme, name):
        t = moods.tune(moods.palette(a, scheme), a, scheme)
        moods.check(t, f"{name} ({scheme})")
        return "".join(f"--{k}:{v};" for k, v in t.items() if k not in unused)

    d = analysed["default"]
    out = ["/* Written by _tools/design.py write_moods(): a palette per picture, from the picture itself. Every text pair is checked for AA. */",
           f":root{{{block(d, 'dark', 'default')}color-scheme:dark}}",
           f':root[data-scheme="light"]{{{block(d, "light", "default")}color-scheme:light}}']
    for name, a in analysed.items():
        out.append(f'[data-mood="{name}"]{{{block(a, "dark", name)}}}')
        out.append(f'[data-scheme="light"][data-mood="{name}"],[data-scheme="light"] [data-mood="{name}"]{{{block(a, "light", name)}}}')
    DESIGN.mkdir(parents=True, exist_ok=True)
    (DESIGN / "moods.css").write_text("\n".join(out) + "\n", encoding="utf-8")
    return len(analysed)

def finish():
    """Every build script ends here: the homepage and the palettes are rebuilt from everything current."""
    import build_home
    build_home.build()
    n = write_moods()
    print(f"homepage rebuilt · assets/design/moods.css: {n} palettes")
