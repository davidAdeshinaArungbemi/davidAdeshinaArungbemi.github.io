"""The pieces the three design directions share: the content as markup, the moods as CSS, the page shell.

The content is the live site's own (see content.py); the colours come from his pictures (moods.py).
Each direction (dir_a.py, dir_b.py, dir_c.py) arranges these pieces in its own way, with its own
stylesheet and a few lines of script. build.py runs them all.
"""
import html, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import content as c                                    # noqa: E402
import moods                                           # noqa: E402

OUT = Path("_directions")
esc, attr = c.esc, c.attr
ARTICLE = "the-narrative-hypothesis"                   # the article shown in every direction
TOPIC = "stories-and-ai"                               # the topic page shown in every direction

# The four research topics keep one hue each across the site (proposed; his to change).
TOPIC_HUES = {"stories-and-ai": 52, "aesthetics": 352, "visualisation": 238, "minds": 298}

# The clips in the showcase, in order (proposed from the three clips the site already has; his to pick).
CLIPS = [("water-town", 14), ("blender-animation", 7), ("robot-arm", 12)]

# ---------------------------------------------------------------- moods used by the pages

class Moods:
    """Collects every mood the pages mention, then writes them as CSS for one direction."""
    def __init__(self):
        self.seen = {"default": moods.fixed(250, 0.0)}
        for slug, hue in TOPIC_HUES.items():
            self.seen[f"topic-{slug}"] = moods.fixed(hue, 0.85, (hue + 32) % 360)

    def of(self, img):
        """The mood name for a picture (registering it)."""
        p = Path(img.lstrip("/"))
        stem = re.sub(r"-(800|1200|1600)$", "", p.stem)
        name = (p.parent.name + "-" + stem) if p.parts[0] == "articles" else stem
        name = re.sub(r"[^a-z0-9-]+", "-", name.lower())
        if name not in self.seen:
            self.seen[name] = moods.analyse(str(p))
        return name

    def info(self, name): return self.seen[name]

    def css(self, default_scheme, tune=None, default_mood="default", auto=False):
        """All moods as custom-property rules. `tune(tokens, analysis, scheme)` lets a direction add or adjust tokens."""
        other = "light" if default_scheme == "dark" else "dark"
        def block(a, scheme, name):
            t = moods.palette(a, scheme)
            if tune: t = tune(t, a, scheme) or t
            moods.check(t, f"{name} ({scheme})")
            return "".join(f"--{k}:{v};" for k, v in t.items())
        d = self.seen[default_mood]
        out = [f":root{{{block(d, default_scheme, 'default')}color-scheme:{default_scheme}}}",
               f":root[data-scheme=\"{other}\"]{{{block(d, other, 'default')}color-scheme:{other}}}"]
        if auto:                                        # without the script, still follow the device
            out.append(f"@media (prefers-color-scheme:{other}){{:root:not([data-scheme]){{{block(d, other, 'default')}color-scheme:{other}}}}}")
        for name, a in self.seen.items():
            out.append(f'[data-mood="{name}"]{{{block(a, default_scheme, name)}}}')
            out.append(f'[data-scheme="{other}"][data-mood="{name}"],[data-scheme="{other}"] [data-mood="{name}"]{{{block(a, other, name)}}}')
        return "\n".join(out) + "\n"

# ---------------------------------------------------------------- links inside a prototype

def linker(here):
    """Internal links that have a page in this prototype go to it; the rest open the current site."""
    home = "index.html" if here != "home" else ""
    table = {f"/{TOPIC}/": f"{TOPIC}.html", f"/articles/{ARTICLE}/": f"{ARTICLE}.html", "/": "index.html"}
    def fix(u):
        if u in table: return table[u]
        if u.startswith("/#"): return (home or "") + u[1:]
        if u.startswith("#") and here != "home": return "index.html" + u
        return u
    return fix

def relink(fragment, fix):
    return re.sub(r'\bhref="([^"]*)"', lambda m: f'href="{attr(fix(html.unescape(m.group(1))))}"', fragment)

# ---------------------------------------------------------------- shared pieces of markup

ICON = {
    "prev": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "next": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "toggle": '<svg class="i-pause" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M8 5v14M16 5v14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>'
              '<svg class="i-play" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg>',
    "scheme": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3.8a8.2 8.2 0 0 0 0 16.4z" fill="currentColor"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    "close": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
}

def tags_html(tags):
    return ('<ul class="tags">' + "".join(f"<li>{esc(t)}</li>" for t in tags) + "</ul>") if tags else ""

def item(p, M, fix, level=3, home=None, lazy=True):
    """One piece in a list: picture, label, title, one line, tags, extra links."""
    mood = M.of(p["img"])
    data = f' data-peek="{mood}"'
    if p["topics"]: data += f' data-topics="{" ".join(p["topics"])}"'
    if p.get("group"): data += f' data-kind="{p["group"]}"'
    if home is not None: data += ' data-home' if home else ' hidden'
    ink = " is-ink" if p.get("ink") else ""
    lazy_attr = ' loading="lazy"' if lazy else ""
    extras = ('<p class="item-extra">' + "".join(f'<a href="{attr(fix(u))}">{esc(t)}</a>' for t, u in p["extras"]) + "</p>") if p["extras"] else ""
    href = attr(fix(p["href"]))
    return (f'<li class="item"{data}>'
            f'<a class="item-thumb{ink}" href="{href}" tabindex="-1" aria-hidden="true"><img src="{attr(p["img"])}" alt="" width="{p["w"]}" height="{p["h"]}"{lazy_attr}></a>'
            f'<div class="item-text"><p class="item-kind">{esc(p["label"])}</p>'
            f'<h{level} class="item-title"><a href="{href}">{esc(p["title"])}</a></h{level}>'
            f'<p class="item-line">{esc(p["line"])}</p>{tags_html(p["tags"])}{extras}</div></li>')

def pub(p, M, fix, level=3, home=None):
    """A publication as the homepage gives it: label, title, citation, what it found, links."""
    mood = M.of(p["img"])
    data = f' data-peek="{mood}" data-topics="{" ".join(p["topics"])}"'
    if home is not None: data += ' data-home' if home else ' hidden'
    return (f'<li class="pub"{data}>'
            f'<a class="pub-thumb" href="{attr(fix(p["href"]))}" tabindex="-1" aria-hidden="true"><img src="{attr(p["img"])}" alt="" width="{p["w"]}" height="{p["h"]}" loading="lazy"></a>'
            f'<div class="pub-text"><p class="item-kind">{esc(p["label"])}</p>'
            f'<h{level} class="pub-title"><a href="{attr(fix(p["href"]))}">{esc(p["title"])}</a></h{level}>'
            f'<p class="pub-cite">{p["cite"]}</p><p class="pub-line">{esc(p["line"])}</p>'
            f'<p class="pub-links">{relink(p["links"], fix)}</p></div></li>')

def topic_tile(t, M, fix, level=3):
    """A research topic: its lead picture, name, one line and how many pieces it holds."""
    lead = next(c.piece(k, key) for k, key in t["start"] if k != "image")
    n = len(set(t["start"]) | set(t["items"]))
    mood = f"topic-{t['slug']}"
    return (f'<li class="topic" data-mood="{mood}" data-peek="{mood}" data-topic="{t["slug"]}">'
            f'<a href="{attr(fix("/" + t["slug"] + "/"))}">'
            f'<span class="topic-art"><img src="{attr(lead["img"])}" alt="" width="{lead["w"]}" height="{lead["h"]}" loading="lazy"></span>'
            f'<span class="topic-title">{esc(t["title"])}</span><span class="topic-line">{esc(t["line"])}</span>'
            f'<span class="topic-count">{n} pieces →</span></a></li>')

def world(p, M, fix, home=None):
    """One picture from Worlds, linking to its place on the Worlds page."""
    mood = M.of(p["img"])
    year = re.search(r"(19|20)\d\d", p["label"])
    data = f' data-peek="{mood}"' + (f' data-topics="{" ".join(p["topics"])}"' if p["topics"] else "")
    if home is not None: data += ' data-home' if home else ' hidden'
    return (f'<figure class="world"{data}>'
            f'<a class="world-media" href="{attr(fix(p["href"]))}"><img src="{attr(p["img"])}" alt="{attr(p["alt"])}" width="{p["w"]}" height="{p["h"]}" loading="lazy"></a>'
            f'<figcaption><strong>{esc(p["title"])}</strong><span class="world-desc">{esc(p["short"])}</span>'
            + (f'<span class="world-year">{year.group(0)}</span>' if year else "") + "</figcaption></figure>")

def showcase(M, fix, colour="page", ambient=False, label_level="p"):
    """The clip showcase. Works as plain posters and links without the script."""
    clips = [(c.piece("image", slug), secs) for slug, secs in CLIPS]
    n = len(clips)
    slides, picks = [], []
    for i, (p, secs) in enumerate(clips):
        v = p["video"]
        mood = M.of(v["poster"])
        fit = "contain" if p["slug"] == "robot-arm" else "cover"
        href = attr(fix(p["href"]))
        hidden = "" if i == 0 else " hidden"
        load = ' fetchpriority="high"' if i == 0 else ' loading="lazy"'
        slides.append(
            f'<figure class="showcase-slide" data-slide data-src="{attr(v["src"])}" data-mood="{mood}" data-seconds="{secs}" data-fit="{fit}" '
            f'data-title="{attr(p["title"])}"{hidden}>'
            f'<div class="showcase-media"><img class="showcase-poster" src="{attr(v["poster"])}" alt="{attr(v["label"])}" width="{v["w"]}" height="{v["h"]}"'
            f'{load}></div>'
            f'<figcaption class="showcase-caption" data-showcase-hold><span class="showcase-count" aria-hidden="true">{i + 1} / {n}</span>'
            f'<{label_level} class="showcase-title"><a href="{href}">{esc(p["title"])}</a></{label_level}>'
            f'<p class="showcase-line">{esc(p["short"])}</p><p class="showcase-meta">{esc(p["label"])}</p></figcaption></figure>')
        picks.append(
            f'<li><a href="{href}" data-showcase-pick aria-label="{attr(p["title"])}">'
            f'<img class="pick-thumb" src="{attr(v["poster"])}" alt="" width="{v["w"]}" height="{v["h"]}" loading="lazy">'
            f'<span class="pick-n" aria-hidden="true">{i + 1}</span><span class="pick-title">{esc(p["title"])}</span>'
            f'<span class="pick-progress" aria-hidden="true"></span></a></li>')
    canvas = '<canvas class="showcase-ambient" data-showcase-ambient width="24" height="15" aria-hidden="true"></canvas>' if ambient else ""
    first_mood = M.of(clips[0][0]["video"]["poster"])
    own = f' data-mood="{first_mood}"' if colour == "self" else ""
    return (f'<section class="showcase" data-showcase data-colour="{colour}"{own} aria-label="Showcase">'
            f'<div class="showcase-stage" data-showcase-stage>{canvas}{"".join(slides)}</div>'
            f'<div class="showcase-bar" data-showcase-hold><div class="showcase-controls">'
            f'<button type="button" data-showcase-prev aria-label="Previous clip">{ICON["prev"]}</button>'
            f'<button type="button" data-showcase-toggle data-state="paused" aria-label="Play the showcase">{ICON["toggle"]}</button>'
            f'<button type="button" data-showcase-next aria-label="Next clip">{ICON["next"]}</button></div>'
            f'<ol class="showcase-picks">{"".join(picks)}</ol></div>'
            f'<p class="visually-hidden" data-showcase-status aria-live="polite"></p></section>'), first_mood

def now_list(H, fix):
    return '<dl class="now">' + "".join(f"<div><dt>{dt}</dt><dd>{relink(dd, fix)}</dd></div>" for dt, dd in H["now"]) + "</dl>"

def hero_art(H, M):
    a = H["art"]
    return (f'<figure class="head-art" data-peek="{M.of(a["src"])}"><img src="{attr(a["src"])}" alt="{attr(a["alt"])}" width="{a["w"]}" height="{a["h"]}" loading="lazy">'
            f'<figcaption>{a["caption"]}</figcaption></figure>')

def contact_list(H, fix):
    return ('<ul class="contact-list">' + "".join(f'<li><span class="contact-label">{label}</span><span>{relink(rest, fix)}</span></li>' for label, rest in H["contact"]) + "</ul>")

def suzume_note(H, fix):
    return f'<div class="suzume" id="suzume"><img src="/assets/img/seal.png" alt="" width="40" height="39"><p>{relink(H["suzume"], fix)}</p></div>'

def also_suzume(H, fix):
    """The second half of the homepage kicker: "also writes as (seal) Suzume"."""
    part = H["kicker"].split("</span>", 1)[1].strip()
    return relink(part, fix)

NAV = [("Research", "/#research"), ("Publications", "/#publications"), ("Articles", "/articles/"),
       ("Projects", "/projects/"), ("Worlds", "/images.html"), ("CV", "/cv.html"), ("Contact", "/#contact")]
HOME_NAV = [("Research", "#research"), ("Publications", "#publications"), ("Articles", "#articles"),
            ("Projects", "#projects"), ("Worlds", "#worlds"), ("CV", "/cv.html"), ("Contact", "#contact")]

def nav_links(here, fix, current=None, cls=""):
    items = HOME_NAV if here == "home" else NAV
    klass = f' class="{cls}"' if cls else ""
    return "".join(f'<a{klass} href="{attr(fix(u))}"' + (' aria-current="page"' if t == current else "") + f">{t}</a>" for t, u in items)

DIRECTIONS = {"a": "The screen", "b": "Four lenses", "c": "Rooms", "d": "A and B mixed"}

def proto_bar(d, here):
    """A strip that belongs to the prototype, not to the design: where you are and how to get around."""
    pages = [("home", "index.html", "Homepage"), ("topic", f"{TOPIC}.html", "Topic page"), ("article", f"{ARTICLE}.html", "Article")]
    links = "".join(f'<a href="{u}"' + (' aria-current="page"' if k == here else "") + f">{t}</a>" for k, u, t in pages)
    return (f'<aside class="proto" aria-label="Prototype"><strong>Direction {d.upper()} · {DIRECTIONS[d]}</strong>{links}'
            f'<a class="proto-all" href="../">All directions</a><span class="proto-note">Only these three pages are built. Other links open the current site.</span></aside>')

# The prototype strip's styles, the skip link and [hidden] live in shared/proto.css.

def page(d, here, title, body, default_scheme, mood="default", extra_head="", body_class=""):
    return f"""<!DOCTYPE html>
<html lang="en" data-direction="{d}" data-default-scheme="{default_scheme}" data-mood="{mood}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#101114" data-follow>
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/seal-32.png">
<link rel="stylesheet" href="../shared/fonts.css">
<link rel="stylesheet" href="../shared/proto.css">
<link rel="stylesheet" href="moods.css">
<link rel="stylesheet" href="{d}.css">
<script src="../shared/scheme.js"></script>
<script src="../shared/mood.js" defer></script>
<script src="../shared/showcase.js" defer></script>
<script src="{d}.js" defer></script>{extra_head}
</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
{proto_bar(d, here)}
{body}
</body>
</html>
"""

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

# ---------------------------------------------------------------- data every direction uses

def gather():
    H = c.homepage()
    exp = [c.piece("article", s) for s in H["home_articles"] if c.is_experiment(c.POST[s])]
    ess = [c.piece("article", s) for s in H["home_articles"] if not c.is_experiment(c.POST[s])]
    return dict(
        H=H,
        selected=c.piece("article", H["selected"]["slug"]),
        experiments=exp, essays=ess,
        projects=[c.piece("project", t) for t in H["home_projects"]],
        worlds=[c.piece("image", s) for s in H["showcase"]],
        all_articles=[c.piece("article", p["slug"]) for p in c.POSTS],
        all_projects=[c.piece("project", p[3]) for p in c.build_cards.PROJECTS],
        topic=c.TOPIC[TOPIC],
        article=c.article_page(ARTICLE),
    )

def topic_sections(t):
    """The same grouping the live topic pages use."""
    started = set(t["start"])
    rest = [i for i in t["items"] if i not in started]
    P = lambda i: c.piece(*i)
    return dict(
        start=[P(i) for i in t["start"]],
        pubs=[P(i) for i in rest if i[0] == "pub"],
        experiments=[P(i) for i in rest if i[0] == "article" and c.is_experiment(c.POST[i[1]])],
        projects=[P(i) for i in rest if i[0] == "project"],
        essays=[P(i) for i in rest if i[0] == "article" and not c.is_experiment(c.POST[i[1]])],
        images=[P(i) for i in rest if i[0] == "image"],
        others=[o for o in c.TOPICS if o is not t],
    )

def article_body(A, M, room=True):
    """The published body, with each figure marked so the page can take its colours while it is in view."""
    def mark(m):
        src = re.search(r'src="([^"]+)"', m.group(0))
        if not src or not src.group(1).startswith("/"): return m.group(0)
        mood = M.of(c.smaller(src.group(1)))
        tag = m.group(1)
        return tag[:-1] + (f' data-room="{mood}"' if room else "") + f' data-peek="{mood}">' + m.group(2)
    return re.sub(r"(<figure[^>]*>)(.*?</figure>)", mark, A["body"], flags=re.S)

