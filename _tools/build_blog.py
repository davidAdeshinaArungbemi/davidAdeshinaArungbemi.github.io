"""The articles, on the site itself: /articles/ (the index) and /articles/<slug>/ (each piece).

Run from the repo root (needs bs4; the miniconda python has it: /opt/miniconda3/bin/python3):
  python3 _tools/build_blog.py            rebuild the article pages, the index, sitemap.xml, then the homepage
  python3 _tools/build_blog.py --import   first copy any new Medium posts from the feed into _writing/

Each article is _writing/<slug>.html: a JSON header inside an HTML comment, then the body as plain
HTML (p, h2, h3, figure, blockquote, pre, lists). Edit them by hand freely; --import never overwrites
one that exists. A post's images live next to its page, in articles/<slug>/, downloaded from Medium
when it's imported. Every page links back to its Medium original.

Header fields: title, date (YYYY-MM-DD), medium (the original's URL), deck (the subtitle, may hold
inline HTML), kind (Essay, Experiment, …), line (one sentence for cards and search results),
tags (topic labels under the card), cover (card image), art (optional larger image for the top of the page), home (show on the homepage).
"""
import argparse, email.utils, html, io, json, math, re, subprocess, urllib.parse
from datetime import date
from pathlib import Path
from PIL import Image
import design
from design import esc, attr

SITE = "https://davidadeshinaarungbemi.github.io"
FEED = "https://medium.com/feed/@suzume1"
MEDIUM = "https://suzume1.medium.com/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
SRC, OUT = Path("_writing"), Path("articles")


# Shorter addresses for posts whose Medium slugs are long; new posts get the first six words
SLUGS = {
    "dream-a-better-dream-6cff36484c35": "dream-a-better-dream",
    "you-are-what-you-prefer-2284ebdf1a00": "you-are-what-you-prefer",
    "in-brightest-day-in-blackest-night-no-evil-shall-escape-my-sight-47d54154abcb": "in-brightest-day",
    "who-deserves-moral-consideration-im-not-sure-anymore-ab2980ac549f": "who-deserves-moral-consideration",
    "gestalt-the-whole-is-not-the-sum-of-its-parts-a4e5f1c61ef1": "gestalt",
    "i-tried-to-build-an-aesthetic-model-of-the-human-brain-i-failed-heres-what-i-learned-13c75644258a": "aesthetic-model",
    "the-narrative-hypothesis-complexity-37bd4417575f": "narrative-hypothesis-complexity",
    "i-ran-the-experiment-here-is-what-i-found-d3052906ac86": "i-ran-the-experiment",
    "the-narrative-hypothesis-f87be35619cf": "the-narrative-hypothesis",
    "inside-qwen-0-5b-a-behavioral-profile-across-32-dimensions-1ead43a6ea3c": "inside-qwen",
}
# Posts whose subtitle Medium's feed gives as an ordinary first paragraph
DECK_IS_FIRST_PARAGRAPH = {"dream-a-better-dream", "aesthetic-model"}

ALLOWED = {"p", "h2", "h3", "figure", "img", "figcaption", "blockquote", "pre", "code", "ul", "ol", "li",
           "a", "strong", "em", "br", "hr", "mark", "iframe"}
KEEP = {"a": {"href"}, "img": {"src", "alt"}, "figure": {"class"},
        "iframe": {"src", "title", "loading", "allow", "allowfullscreen", "style"}}



# ------------------------------------------------------------------ importing from Medium

def fetch(url):
    return subprocess.run(["curl", "-sSL", "--fail", "-A", UA, url], capture_output=True, check=True).stdout

def blocks(soup):
    return [el for el in soup.contents if getattr(el, "name", None)]

def embed(soup, src):
    """Medium wraps videos in an embed.ly frame; use the player itself, or a plain link."""
    url = (urllib.parse.parse_qs(urllib.parse.urlparse(src).query).get("url") or [src])[0]
    vimeo = re.search(r"vimeo\.com/(?:video/)?(\d+)", url)
    youtube = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})", url)
    if not (vimeo or youtube):
        p, a = soup.new_tag("p"), soup.new_tag("a", href=url)
        a.string = url
        p.append(a)
        return p
    player = (f"https://player.vimeo.com/video/{vimeo.group(1)}?dnt=1" if vimeo
              else f"https://www.youtube-nocookie.com/embed/{youtube.group(1)}")
    fig = soup.new_tag("figure", attrs={"class": "embed"})
    fig.append(soup.new_tag("iframe", attrs={"src": player, "title": "Video", "loading": "lazy",
                                             "allow": "fullscreen; picture-in-picture", "allowfullscreen": ""}))
    return fig

def clean(body, from_feed):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(body, "html.parser")
    if from_feed:  # the feed marks big headings h3 and small ones h4; the site uses h2 and h3
        for h in soup.find_all("h3"): h.name = "h2"
        for h in soup.find_all("h4"): h.name = "h3"
    for img in soup.find_all("img"):
        if "/_/stat" in img.get("src", ""): img.decompose()           # Medium's view counter
    for h in soup.find_all(["h2", "h3"]):
        if re.search(r"in\s+your\s+inbox", h.get_text(), re.I): h.decompose()   # its newsletter prompt
    for pre in soup.find_all("pre"):                                   # code: plain text, line breaks kept
        for br in pre.find_all("br"): br.replace_with("\n")
        text = pre.get_text()
        pre.clear()
        code = soup.new_tag("code")
        code.string = text
        pre.append(code)
    for f in soup.find_all("iframe"):
        if not f.get("src", "").startswith(("https://player.vimeo.com/", "https://www.youtube-nocookie.com/")):
            f.replace_with(embed(soup, f.get("src", "")))
    for t in soup.find_all(True):
        if t.name not in ALLOWED:
            t.unwrap()
            continue
        t.attrs = {k: v for k, v in t.attrs.items() if k in KEEP.get(t.name, set())}
    for t in soup.find_all(["p", "h2", "h3", "li", "figcaption"]):
        if not t.get_text(strip=True) and not t.find(["img", "iframe"]): t.decompose()
    return soup

def take_deck(soup, first_paragraph):
    """Medium's subtitle sits at the top of the body: a small heading, or a line set in italics."""
    deck = ""
    for el in blocks(soup)[:4]:
        if el.name in ("figure", "hr"): continue
        parts = [c for c in el.contents if not (isinstance(c, str) and not c.strip())]
        italic = el.name == "p" and parts and all(getattr(c, "name", None) == "em" for c in parts)
        if el.name == "h3" or italic or (first_paragraph and el.name == "p"):
            deck = "".join(c.decode_contents() for c in parts) if italic else el.decode_contents()
            el.decompose()
        break
    for el in blocks(soup):                       # rules left at the very top separate nothing
        if el.name == "figure": continue
        if el.name == "hr": el.decompose(); continue
        break
    return deck.strip()

def localise(soup, slug):
    folder = OUT / slug
    folder.mkdir(parents=True, exist_ok=True)
    saved = []
    for n, img in enumerate(soup.find_all("img"), 1):
        m = re.search(r"(?:cdn-images-1|miro)\.medium\.com/.*?([^/?#]+)$", img.get("src", ""))
        if not m: continue
        data = fetch(f"https://cdn-images-1.medium.com/max/2000/{m.group(1)}")
        im = Image.open(io.BytesIO(data))
        if getattr(im, "is_animated", False):
            name = f"{n:02d}.gif"
            (folder / name).write_bytes(data)
        else:
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                flat = Image.new("RGB", im.size, "white")
                flat.paste(im, mask=im.split()[3])
                im = flat
            im = im.convert("RGB")
            if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
            name = f"{n:02d}.jpg"
            im.save(folder / name, quality=84, optimize=True, progressive=True)
            if im.width > 900:
                im.resize((800, round(im.height * 800 / im.width)), Image.LANCZOS).save(
                    folder / f"{n:02d}-800.jpg", quality=82, optimize=True, progressive=True)
        img["src"] = f"/{OUT}/{slug}/{name}"
        saved.append(img["src"])
    return saved

def summary(deck, soup):
    from bs4 import BeautifulSoup
    text = BeautifulSoup(deck, "html.parser").get_text() if deck else next(
        (p.get_text() for p in soup.find_all("p") if len(p.get_text()) > 60), "")
    first = re.split(r"(?<=[.?!])\s", text.strip(), maxsplit=1)[0]
    return first if len(first) < 180 else first[:177].rsplit(" ", 1)[0] + "…"

def write_post(path, meta, body):
    path.write_text("<!--\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n-->\n" + body.strip() + "\n", encoding="utf-8")

def import_post(slug, title, published, medium, body, from_feed):
    path = SRC / f"{slug}.html"
    if path.exists():
        return False
    soup = clean(body, from_feed)
    deck = take_deck(soup, slug in DECK_IS_FIRST_PARAGRAPH)
    images = localise(soup, slug)
    meta = dict(title=title, date=published, medium=medium, deck=deck, kind="Essay", line=summary(deck, soup),
                cover=images[0] if images else "", home=False)
    SRC.mkdir(exist_ok=True)
    write_post(path, meta, "\n".join(el.decode(formatter="minimal") for el in blocks(soup)))
    print(f"imported {slug} ({len(images)} images) — check its kind, line and cover in {path}")
    return True

def import_feed():
    xml = fetch(FEED).decode("utf-8")
    new = 0
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        link = re.search(r"<link>(.*?)</link>", item).group(1).split("?")[0]
        key = link.rstrip("/").rsplit("/", 1)[-1]
        slug = SLUGS.get(key) or "-".join(re.sub(r"-[0-9a-f]{10,12}$", "", key).split("-")[:6])
        title = html.unescape(re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", item, re.S).group(1)).strip()
        published = email.utils.parsedate_to_datetime(re.search(r"<pubDate>(.*?)</pubDate>", item).group(1)).date().isoformat()
        body = re.search(r"<content:encoded><!\[CDATA\[(.*?)\]\]></content:encoded>", item, re.S).group(1)
        new += import_post(slug, title, published, link, body, from_feed=True)
    print(f"{new} new post(s) from Medium")


# ------------------------------------------------------------------ building the pages

def load_all():
    posts = []
    for path in SRC.glob("*.html"):
        text = path.read_text(encoding="utf-8")
        m = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
        if not m:
            raise SystemExit(f"{path}: no JSON header in an HTML comment at the top")
        meta = json.loads(m.group(1))
        meta["slug"], meta["body"] = path.stem, text[m.end():]
        check_header(meta, path)
        posts.append(meta)
    return sorted(posts, key=lambda p: p["date"], reverse=True)

def check_header(meta, path):
    """Stop with a plain message, naming the file, when a header can't make a page."""
    for key in ("title", "date", "medium", "kind", "line", "cover"):
        if not meta.get(key):
            raise SystemExit(f"{path}: the header needs \"{key}\"" + (" (an image for the article's card; a post with no images needs one chosen by hand)" if key == "cover" else ""))
    try:
        date.fromisoformat(meta["date"])
    except ValueError:
        raise SystemExit(f"{path}: the date \"{meta['date']}\" isn't YYYY-MM-DD")
    for key in ("cover", "art"):
        if meta.get(key) and not Path(meta[key].lstrip("/")).exists():
            raise SystemExit(f"{path}: {key} {meta[key]} doesn't exist")

def day(d): return date.fromisoformat(d).strftime("%-d %b %Y")
def month(d): return date.fromisoformat(d).strftime("%b %Y")
def plain(s):
    from bs4 import BeautifulSoup
    return BeautifulSoup(s, "html.parser").get_text()
def size(src): return Image.open(src.lstrip("/")).size
def smaller(src):
    """The 800px copy of an image, if there is one."""
    p = Path(src.lstrip("/"))
    s = p.with_name(p.stem + "-800" + p.suffix)
    return "/" + str(s) if s.exists() else src
def mid(src):
    """The 1200px copy of an image, if there is one."""
    p = Path(src.lstrip("/"))
    s = p.with_name(p.stem + "-1200" + p.suffix)
    return "/" + str(s) if s.exists() else None

def prepare(post, links):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(post["body"], "html.parser")
    for a in soup.find_all("a", href=True):                 # links between the articles stay on the site
        a["href"] = links.get(a["href"].split("?")[0].rstrip("/"), a["href"])
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith("/"):
            if not Path(src.lstrip("/")).exists():
                raise SystemExit(f"{post['slug']}: image {src} is missing")
            w, h = size(src)
            img["width"], img["height"] = str(w), str(h)
            if smaller(src) != src:
                steps = [f"{smaller(src)} 800w"] + ([f"{mid(src)} 1200w"] if mid(src) else []) + [f"{src} {w}w"]
                img["srcset"] = ", ".join(steps)
                img["sizes"] = "(min-width: 940px) 900px, 100vw"
        img["loading"], img["decoding"] = "lazy", "async"
    for fig in soup.find_all("figure"):                     # a mat in the picture's own colours
        img = fig.find("img")
        if img and img.get("src", "").startswith("/"):
            fig["data-mood"] = design.mood_name(img["src"])
    first = next((el for el in blocks(soup) if el.name not in ("figure", "hr")), None)
    if first is not None and first.name == "p" and len(first.get_text()) > 160 and first.get_text().strip()[:1].isalpha():
        first["class"] = "opening"                       # gets the drop cap
    lead_figure = bool(blocks(soup)) and blocks(soup)[0].name == "figure"
    if lead_figure:
        lead_img = blocks(soup)[0].find("img")
        if lead_img:
            lead_img["loading"], lead_img["fetchpriority"] = "eager", "high"
    words = len(soup.get_text(" ").split())
    return soup.decode(formatter="minimal"), lead_figure, max(1, math.ceil(words / 230))

def neighbour(post, label):
    if not post: return "<span></span>"
    img = smaller(post["cover"])
    w, h = size(img)
    slug, title = post["slug"], post["title"]
    return (f'<a class="near" href="/articles/{slug}/" data-own="{design.mood_name(img)}"><img src="{img}" alt="" width="{w}" height="{h}" loading="lazy">'
            f'<span><span class="item-kind">{label}</span><span class="near-title">{esc(title)}</span></span></a>')

def topics_of(slug):
    from build_topics import TOPICS
    return [t for t in TOPICS if ("article", slug) in set(t["start"]) | set(t["items"])]

def og_image(post, art):
    """A landscape copy for link previews when the art is portrait or square."""
    w, h = size(art)
    if h / w <= 0.9:
        return art
    out = OUT / post["slug"] / "cover-og.jpg"
    ow = min(w, 1200)
    oh = round(ow / 1.91)
    with Image.open(art.lstrip("/")) as im:
        im = im.convert("RGB").resize((ow, round(h * ow / w)), Image.LANCZOS)
        top = (im.height - oh) // 2
        im.crop((0, top, ow, top + oh)).save(out, quality=84, optimize=True, progressive=True)
    return "/" + str(out)

def render_post(post, links, newer, older):
    body, lead_figure, minutes = prepare(post, links)
    url = f"{SITE}/articles/{post['slug']}/"
    deck = f'\n    <p class="post-deck">{post["deck"]}</p>' if post.get("deck") else ""
    art = post.get("art") or post.get("cover")
    cover = ""
    if art and not lead_figure and art not in post["body"]:    # a picture already in the text isn't shown twice
        w, h = size(art)
        cover = f'\n  <figure class="post-cover" data-mood="{design.mood_name(art)}"><img src="{art}" alt="" width="{w}" height="{h}"></figure>'
    og = og_image(post, art or post["cover"])
    data = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": post["title"],
            "datePublished": post["date"], "url": url, "image": SITE + og,
            "description": post["line"], "isBasedOn": post["medium"],
            "author": {"@type": "Person", "name": "David Adeshina Arungbemi", "alternateName": "Suzume", "url": SITE + "/"}}
    ld = f'\n<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
    topics = topics_of(post["slug"])                         # the page wears its first topic's colours
    mood = f"topic-{topics[0]['slug']}" if topics else "default"
    strip = ""
    if topics:
        tabs = "".join(f'<a class="tab" href="/{t["slug"]}/" data-mood="topic-{t["slug"]}">{esc(t["title"])}</a>' for t in topics)
        strip = f'\n  <nav class="topic-strip" aria-label="Topics of this article"><div class="post-wrap"><span class="tabs-label" aria-hidden="true">Topics</span>{tabs}</div></nav>'
    meta = design.meta(f"{post['title']} · Suzume", post["line"], url, og, og_type="article", published=post["date"], extra=ld)
    return (design.head(meta, mood=mood, rss=True) + '<div class="read-progress" aria-hidden="true"></div>\n' + design.header(current="Articles") + f"""
<main id="main" class="post">
<article>
  <header class="post-head"><div class="post-wrap">
    <p class="post-kicker"><a href="/articles/">Articles</a> <span aria-hidden="true">·</span> {esc(post['kind'])} <span aria-hidden="true">·</span> <time datetime="{post['date']}">{day(post['date'])}</time> <span aria-hidden="true">·</span> {minutes} min read</p>
    <h1>{esc(post['title'])}</h1>{deck}
    <p class="post-byline"><img src="/assets/img/seal-64.png" alt="" width="22" height="22"> Suzume <span>· David Adeshina Arungbemi</span></p>
  </div></header>{strip}{cover}
  <div class="post-body">
{body}
    <p class="post-end"><img src="/assets/img/seal-64.png" alt="" width="30" height="30" loading="lazy"></p>
  </div>
  <footer class="post-foot">
    <p class="post-origin">First published on Medium. <a href="{post['medium']}">Read it there →</a></p>
    <nav class="nears" aria-label="More articles">{neighbour(newer, 'Newer')}{neighbour(older, 'Older')}</nav>
    <p class="more"><a href="/articles/">All articles →</a></p>
  </footer>
</article>
</main>
""" + design.footer() + "\n" + design.END)

def post_card(p):
    group = "experiment" if "experiment" in p["kind"].lower() else "essay"
    return design.card(f"/articles/{p['slug']}/", smaller(p["cover"]), f"{p['kind']} · {month(p['date'])}", p["title"], p["line"],
                       p.get("tags", ()), group=group)

def render_index(posts):
    latest, rest = posts[0], posts[1:]
    feature = design.feature(f"/articles/{latest['slug']}/", smaller(latest["cover"]), f"Latest · {month(latest['date'])}", latest["title"],
                             latest["line"], latest.get("tags", ()), ink=bool(latest.get("ink")), home=None, level=2)
    choices = design.filters("Show", [("all", "All", None), ("essay", "Essays", None), ("experiment", "Experiments", None)])
    meta = design.meta("Articles · David Adeshina Arungbemi", "Essays and experiment write-ups by David Adeshina Arungbemi, who writes as Suzume.",
                       f"{SITE}/articles/", latest["cover"])
    return design.listed(design.head(meta, rss=True) + design.header(current="Articles") + f"""
<main id="main">
<section class="page-head"><div class="wrap">
  <h1>Articles</h1>
  <p>Essays and write-ups of my experiments, published under my pen name, Suzume (雀, sparrow). Everything here first appeared on <a href="{MEDIUM}">Medium</a>. Papers are under <a href="/#publications">Publications</a>.</p>
  {choices}
</div></section>

<section class="sec latest-sec"><div class="wrap">
  {feature}
  <ol class="cards" data-filterable>{"".join(post_card(p) for p in rest)}</ol>
  <p class="more"><a href="{MEDIUM}">Suzume on Medium →</a></p>
</div></section>
</main>
""" + design.footer() + "\n" + design.END)

def write_sitemap(posts):
    """sitemap.xml at the root: the public pages only, never for/, docs/ or Notebooks/."""
    pages = ["/", "/images.html", "/cv.html", "/articles/",
             "/aesthetics/", "/minds/", "/projects/", "/stories-and-ai/", "/visualisation/"]
    urls = [f"  <url><loc>{SITE}{page}</loc></url>" for page in pages]
    urls += [f"  <url><loc>{SITE}/articles/{p['slug']}/</loc><lastmod>{p['date']}</lastmod></url>" for p in posts]
    Path("sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")

def build():
    design.write_moods()                                    # first, so every page names the current palettes file
    posts = load_all()
    links = {p["medium"].rstrip("/"): f"/articles/{p['slug']}/" for p in posts}
    for i, p in enumerate(posts):
        page = render_post(p, links, posts[i - 1] if i else None, posts[i + 1] if i + 1 < len(posts) else None)
        (OUT / p["slug"]).mkdir(parents=True, exist_ok=True)
        (OUT / p["slug"] / "index.html").write_text(page, encoding="utf-8")
    (OUT / "index.html").write_text(render_index(posts), encoding="utf-8")
    write_sitemap(posts)
    print(f"articles/: {len(posts)} articles · sitemap.xml: {9 + len(posts)} pages")
    design.finish()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--import", dest="do_import", action="store_true", help="copy new Medium posts into _writing/ first")
    if ap.parse_args().do_import:
        import_feed()
    build()
