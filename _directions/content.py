"""The site's real content, read from the same sources the live build uses, for the direction prototypes.

Nothing here is rewritten: titles, lines, statements and captions come from _tools/build_cards.py,
_tools/build_gallery.py, _tools/build_topics.py, the _writing/ headers, and the built index.html and
article pages. Run from the repo root.
"""
import ast, html, json, re, sys
from pathlib import Path
from datetime import date
from PIL import Image

sys.path.insert(0, "_tools")
import build_cards, build_gallery                      # noqa: E402  (plain data + PIL only)

esc = lambda s: html.escape(s, quote=False)
attr = lambda s: html.escape(s, quote=True)
SITE = "https://davidadeshinaarungbemi.github.io"
MEDIUM = "https://suzume1.medium.com/"

def absolute(u):
    """Site-absolute form of a link or image address written relative to the site root."""
    return u if u.startswith(("http://", "https://", "/", "#", "mailto:")) else "/" + u

def absolutise(fragment):
    """Make every href/src in a piece of the homepage's HTML site-absolute (in-page #anchors stay)."""
    return re.sub(r'\b(href|src)="([^"]*)"', lambda m: f'{m.group(1)}="{absolute(m.group(2))}"', fragment)

def size(src):
    with Image.open(src.lstrip("/")) as im:
        return im.size

def month(d): return date.fromisoformat(d).strftime("%b %Y")

def smaller(src):
    p = Path(src.lstrip("/"))
    s = p.with_name(p.stem + "-800" + p.suffix)
    return "/" + str(s) if s.exists() else src

# ---------------------------------------------------------------- build_topics.py without bs4

def _topics_source():
    src = Path("_tools/build_topics.py").read_text(encoding="utf-8")
    ns = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("STATEMENT", "PUBS", "TOPICS"):
            exec(ast.get_source_segment(src, node), ns)
    return ns["STATEMENT"], ns["PUBS"], ns["TOPICS"]

STATEMENT, PUBS, TOPICS = _topics_source()
TOPIC = {t["slug"]: t for t in TOPICS}

# ---------------------------------------------------------------- articles

def load_posts():
    posts = []
    for path in Path("_writing").glob("*.html"):
        text = path.read_text(encoding="utf-8")
        m = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
        meta = json.loads(m.group(1))
        meta["slug"] = path.stem
        posts.append(meta)
    return sorted(posts, key=lambda p: p["date"], reverse=True)

POSTS = load_posts()
POST = {p["slug"]: p for p in POSTS}
PROJ = {p[3]: p for p in build_cards.PROJECTS}
IMAGES = {it[0]: it for _, _, _, items in build_gallery.GROUPS for it in items}
VIDEOS = build_gallery.VIDEOS

def is_experiment(p): return "experiment" in p["kind"].lower()

# ---------------------------------------------------------------- one record per piece

def _topics_of(kind, key):
    return [t["slug"] for t in TOPICS if (kind, key) in set(t["start"]) | set(t["items"])]

def slugify(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def piece(kind, key):
    """kind is 'pub', 'article', 'project' or 'image'; key as in build_topics.TOPICS."""
    if kind == "pub":
        link, img, label, title, line, tags, extras = PUBS[key]
        rec = dict(id=f"pub-{key}", href=link, img=absolute(img), label=label, title=title, line=line,
                   tags=list(tags), extras=[(t, absolute(u)) for t, u in extras])
    elif kind == "article":
        p = POST[key]
        rec = dict(id=f"article-{key}", href=f"/articles/{key}/", img=smaller(p["cover"]),
                   label=f"{p['kind']} · {month(p['date'])}", title=p["title"], line=p["line"],
                   tags=list(p.get("tags", ())), extras=[], group="experiment" if is_experiment(p) else "essay",
                   ink=bool(p.get("ink")), date=p["date"])
    elif kind == "project":
        link, img, label, title, line, extras = PROJ[key]
        rec = dict(id=f"project-{slugify(title)}", href=absolute(link), img=absolute(img), label=label, title=title,
                   line=line, tags=list(build_cards.TAGS[title]), extras=[(t, absolute(u)) for t, u in extras])
    else:
        slug, title, meta, caption, alt = IMAGES[key]
        video = VIDEOS.get(slug)
        img = "/" + video[1] if video else f"/assets/gallery/{slug}-800.jpg"
        rec = dict(id=f"image-{slug}", href=f"/images.html#{slug}", img=img, label=meta, title=title, line=caption,
                   tags=[], extras=[], alt=alt or (video[4] if video else title), slug=slug,
                   short=build_gallery.SHORT.get(slug, caption))
        if video:
            rec["video"] = dict(src="/" + video[0], poster="/" + video[1], w=video[2], h=video[3], label=video[4])
    rec.setdefault("group", None)
    rec["kind"], rec["key"] = kind, key
    rec["w"], rec["h"] = size(rec["img"])
    rec["topics"] = _topics_of(kind, key)
    return rec

# ---------------------------------------------------------------- the homepage, read from index.html

def _one(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    assert m, f"index.html: nothing matches {pattern!r}"
    return m.group(1).strip()

def homepage():
    page = Path("index.html").read_text(encoding="utf-8")
    hero = _one(r'<section class="hero" id="top">(.*?)</section>', page)
    art = re.search(r'<img src="([^"]+)" alt="([^"]*)" width="(\d+)" height="(\d+)"', _one(r'<figure class="hero-art">(.*?)</figure>', hero))
    pubs = []
    for li in re.findall(r'<li class="pub">(.*?)</li>', _one(r'<ol class="pubs">(.*?)</ol>', page), re.S):
        thumb = re.search(r'<a class="pub-thumb" href="([^"]+)"[^>]*><img src="([^"]+)"', li)
        title = re.search(r'<h3 class="pub-title"><a href="([^"]+)">(.*?)</a></h3>', li, re.S)
        img = absolute(thumb.group(2))
        w, h = size(img)
        key = "preprint" if "zenodo" in thumb.group(1) else "gestures"
        pubs.append(dict(id=f"pub-{key}", key=key, kind="pub", group=None, href=title.group(1), img=img, w=w, h=h,
                         label=html.unescape(_one(r'<p class="pub-kind">(.*?)</p>', li)), title=html.unescape(title.group(2)),
                         cite=_one(r'<p class="pub-cite">(.*?)</p>', li), line=html.unescape(_one(r'<p class="pub-line">(.*?)</p>', li)),
                         links=_one(r'<p class="pub-links">(.*?)</p>', li), tags=list(PUBS[key][5]), extras=[],
                         topics=_topics_of("pub", key)))
    sel = _one(r'<div class="w latest">(.*?)</div>\s*<!-- cards:articles -->', page)
    sel_slug = _one(r'<a href="articles/([^/"]+)/"', sel)
    contact = _one(r'<section class="contact" id="contact">(.*?)</section>', page)
    return dict(
        kicker=absolutise(_one(r'<p class="kicker">(.*?)</p>', hero)),
        h1=_one(r"<h1>(.*?)</h1>", hero),
        deck=_one(r'<p class="deck">(.*?)</p>', hero),
        now=[(dt, absolutise(dd)) for dt, dd in re.findall(r"<div><dt>(.*?)</dt><dd>(.*?)</dd></div>", hero, re.S)],
        art=dict(src=absolute(art.group(1)), alt=html.unescape(art.group(2)), w=int(art.group(3)), h=int(art.group(4)),
                 caption=_one(r"<figcaption>(.*?)</figcaption>", hero)),
        statement=_one(r'<p class="research-statement">(.*?)</p>', page),
        pubs=pubs,
        suzume=absolutise(_one(r'<div class="suzume-note" id="suzume">.*?<p>(.*?)</p>', page)),
        selected=dict(slug=sel_slug, label=html.unescape(_one(r'<p class="w-kind">(.*?)</p>', sel))),
        home_articles=re.findall(r'<h3 class="row-title"><a href="/articles/([^/"]+)/">', _one(r"<!-- cards:articles -->(.*?)<!-- /cards:articles -->", page)),
        home_projects=list(build_cards.HOME),
        all_projects=_one(r'<a href="projects/">(All \d+ projects →)</a>', page),
        worlds_intro=_one(r'<p class="images-intro">(.*?)</p>', page),
        worlds_all=_one(r'<a href="images.html">(See all \d+ pieces →)</a>', page),
        showcase=list(build_gallery.SHOWCASE),
        contact_lede=_one(r'<p class="contact-lede">(.*?)</p>', contact),
        contact=[(label, absolutise(rest)) for label, rest in re.findall(r'<li><span class="mono">(.*?)</span>(.*?)</li>', contact, re.S)],
        foot=absolutise(_one(r'<footer class="foot">\s*<p>(.*?)</p>', page)),
    )

# ---------------------------------------------------------------- one built article page

def article_page(slug):
    """The pieces of an already built article page: its text is used exactly as published."""
    page = Path(f"articles/{slug}/index.html").read_text(encoding="utf-8")
    body = _one(r'<div class="post-body">\n(.*?)\n\s*<p class="post-end">', page)
    near = []
    for m in re.finditer(r'<a class="post-near" href="([^"]+)">\s*<img src="([^"]+)"[^>]*>\s*<span><span class="post-near-label">(.*?)</span>'
                         r'<span class="post-near-title">(.*?)</span></span>', page, re.S):
        near.append(dict(href=m.group(1), img=m.group(2), label=m.group(3), title=m.group(4)))
    cover = re.search(r'<figure class="post-cover"><img src="([^"]+)" alt="" width="(\d+)" height="(\d+)">', page)
    return dict(
        slug=slug, post=POST[slug],
        head=_one(r"<head>(.*?)</head>", page),
        kicker=_one(r'<p class="post-kicker">(.*?)</p>', page),
        h1=_one(r"<h1>(.*?)</h1>", page),
        deck=(re.search(r'<p class="post-deck">(.*?)</p>', page, re.S) or [None, ""])[1],
        byline=_one(r'<p class="post-byline">(.*?)</p>', page),
        cover=dict(src=cover.group(1), w=int(cover.group(2)), h=int(cover.group(3))) if cover else None,
        body=body,
        origin=_one(r'<p class="post-origin">(.*?)</p>', page),
        near=near,
    )
