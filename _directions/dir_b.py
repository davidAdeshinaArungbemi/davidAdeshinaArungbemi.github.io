"""Direction B, "Four lenses": his work seen through his four research topics.

The page is organised around the topics. Choosing one (a lens) recolours the whole page in that topic's
colours and brings that topic's work forward in every section. The clip showcase colours only its own frame,
so the page's colour always means "which topic am I looking through". Pieces colour only themselves when
pointed at. Flat, crisp, thick colour rules, grids of cards.
"""
import re
import kit, content as c
from kit import esc, attr

D, SCHEME = "b", "light"
GITHUB_SUZUME, GITHUB_DAVID = "https://github.com/suzume-hue", "https://github.com/davidAdeshinaArungbemi"

# ---------------------------------------------------------------- small helpers

def own(fragment):
    """In B the page's colour belongs to the lens, so a piece colours only itself: data-peek becomes data-own."""
    return fragment.replace(' data-peek="', ' data-own="', 1)

def no_peek(fragment):
    return re.sub(r' data-peek="[^"]*"', "", fragment, count=1)

def item(p, M, fix, level=3, home=None):
    return own(kit.item(p, M, fix, level, home=home))

def pub(p, M, fix, level=3, home=None):
    return own(kit.pub(p, M, fix, level, home=home))

def world(p, M, fix, home=None):
    """A picture at its own proportions: --r is width over height, so a row of them shares one height."""
    s = own(kit.world(p, M, fix, home=home))
    return s.replace('<figure class="world"', f'<figure class="world" style="--r:{p["w"] / p["h"]:.3f}"', 1)

def cards(ps, M, fix, level=3, cls="", home=None):
    """home: a set of ids that show without a lens (None for a page with no lens)."""
    out = []
    for p in ps:
        h = None if home is None else (p["id"] in home)
        out.append(item(p, M, fix, level, home=h))
    return f'<ol class="cards{cls}">' + "".join(out) + "</ol>"

def more(links):
    return '<p class="more">' + "".join(f'<a href="{attr(u)}">{t}</a>' for t, u in links) + "</p>"

def feature(sel, label, M, fix, home=True):
    mood = M.of(sel["img"])
    ink = " is-ink" if sel.get("ink") else ""
    href = attr(fix(sel["href"]))
    keep = " data-home" if home else " hidden"
    return (f'<div class="feature" data-own="{mood}" data-topics="{" ".join(sel["topics"])}"{keep}>'
            f'<a class="feature-art{ink}" href="{href}" tabindex="-1" aria-hidden="true"><img src="{attr(sel["img"])}" alt="" width="{sel["w"]}" height="{sel["h"]}" loading="lazy"></a>'
            f'<div class="feature-text"><p class="item-kind">{esc(label)}</p>'
            f'<h3 class="feature-title"><a href="{href}">{esc(sel["title"])}</a></h3>'
            f'<p class="feature-line">{esc(sel["line"])}</p>{kit.tags_html(sel["tags"])}</div></div>')

# ---------------------------------------------------------------- page furniture

def top(H, here, fix, current=None):
    return (f'<header class="b-head"><div class="wrap">'
            f'<div class="b-head-row"><a class="b-name" href="{attr(fix("/"))}">David Adeshina Arungbemi</a>'
            f'<span class="b-also">{kit.also_suzume(H, fix)}</span>'
            f'<button class="icon-btn" type="button" data-scheme-toggle hidden aria-label="Switch to dark">{kit.ICON["scheme"]}</button></div>'
            f'<nav class="b-nav" aria-label="Sections">{kit.nav_links(here, fix, current)}</nav>'
            f'</div></header>')

def foot(H, here, fix):
    back = "" if here == "home" else f' <a href="{attr(fix("/"))}">Back to the site →</a>'
    return (f'<footer class="b-foot"><div class="wrap"><nav class="foot-nav" aria-label="Site">{kit.nav_links(here, fix)}</nav>'
            f'<p>{H["foot"]}{back}</p></div></footer>')

def sec(id_, title, inner, lensed=False, extra_head=""):
    """One section: a thick rule, the heading, and (under a lens) how much of it is showing."""
    ident = f' id="{id_}"' if id_ else ""
    if lensed:
        count = '<p class="lens-count" data-lens-count hidden></p>'
        empty = '<p class="lens-empty" data-lens-empty hidden>Nothing here for this topic.</p>'
        return (f'<section class="b-sec"{ident} data-lens-section><div class="wrap"><div class="sec-head"><h2>{title}</h2>{count}</div>'
                f'{extra_head}{empty}{inner}</div></section>')
    return f'<section class="b-sec"{ident}><div class="wrap"><div class="sec-head"><h2>{title}</h2></div>{extra_head}{inner}</div></section>'

# ---------------------------------------------------------------- the homepage

def lens_bar(fix):
    buttons = ['<button class="lens-btn" type="button" aria-pressed="true" data-lens-pick="all">All</button>']
    for t in c.TOPICS:
        m = f"topic-{t['slug']}"
        buttons.append(f'<button class="lens-btn" type="button" aria-pressed="false" data-lens-pick="{t["slug"]}" data-mood="{m}" data-peek="{m}" '
                       f'data-title="{attr(t["title"])}" data-href="{attr(fix("/" + t["slug"] + "/"))}">{esc(t["title"])}</button>')
    return ('<div class="lens" data-lens hidden><div class="wrap lens-inner">'
            f'<div class="lens-group" role="group" aria-label="Show work from"><span class="lens-label" aria-hidden="true">Show work from</span>{"".join(buttons)}</div>'
            '<p class="lens-go" data-lens-go hidden><a href="#" data-lens-link>Topic page →</a></p>'
            '<p class="visually-hidden" role="status" data-lens-status></p></div></div>')

def home(data, M):
    H, fix = data["H"], kit.linker("home")
    show, _first = kit.showcase(M, fix, colour="self")
    sel_key = H["selected"]["slug"]
    sel = data["selected"]

    # every piece the lens can bring forward; the ones with data-home are the homepage's own selection
    home_art = set(H["home_articles"])
    exp = [p for p in data["all_articles"] if p["key"] != sel_key and p["group"] == "experiment"]
    ess = [p for p in data["all_articles"] if p["key"] != sel_key and p["group"] != "experiment"]
    art_home = {p["id"] for p in data["all_articles"] if p["key"] in home_art}
    first = {k: i for i, k in enumerate(H["home_projects"])}
    projects = sorted(data["all_projects"], key=lambda p: first.get(p["key"], 99))
    proj_home = {p["id"] for p in projects if p["key"] in first}
    world_slugs = {p["slug"] for p in data["worlds"]}
    extra_images, seen = [], set(world_slugs)
    for t in c.TOPICS:
        for kind, key in list(t["start"]) + [i for i in t["items"] if i not in t["start"]]:
            if kind == "image" and key not in seen:
                seen.add(key)
                extra_images.append(c.piece("image", key))
    walls = "".join(world(p, M, fix, home=True) for p in data["worlds"]) + "".join(world(p, M, fix, home=False) for p in extra_images)
    pubs = "".join(pub(p, M, fix, home=True) for p in H["pubs"])
    tiles = "".join(no_peek(kit.topic_tile(t, M, fix)) for t in c.TOPICS)

    pubs_html = sec("publications", "Publications", f'<ol class="cards pubs">{pubs}</ol>', lensed=True)
    articles_inner = (kit.suzume_note(H, fix)
                      + feature(sel, H["selected"]["label"], M, fix)
                      + f'<div class="group" data-lens-group><h3 class="group-title">Experiments</h3>{cards(exp, M, fix, 4, home=art_home)}</div>'
                      + f'<div class="group" data-lens-group><h3 class="group-title">Essays</h3>{cards(ess, M, fix, 4, home=art_home)}</div>'
                      + more([("All articles →", "/articles/"), ("Suzume on Medium →", c.MEDIUM)]))
    articles_html = sec("articles", "Articles", articles_inner, lensed=True)
    projects_html = sec("projects", "Projects", cards(projects, M, fix, 3, home=proj_home)
                        + more([(H["all_projects"], "/projects/"), ("GitHub as Suzume →", GITHUB_SUZUME), ("GitHub as David →", GITHUB_DAVID)]), lensed=True)
    worlds_html = sec("worlds", "Worlds", f'<div class="wall">{walls}</div>' + more([(H["worlds_all"], "/images.html")]),
                      lensed=True, extra_head=f'<p class="lead">{H["worlds_intro"]}</p>')

    body = f"""{top(H, "home", fix)}
<main id="main">
<section class="b-intro" id="top"><div class="wrap b-intro-grid">
  <div class="b-intro-text">
    <h1>{H["h1"]}</h1>
    <p class="b-deck">{H["deck"]}</p>
  </div>
  {show}
</div></section>

<div class="b-now"><div class="wrap b-now-grid">
  {kit.now_list(H, fix)}
  {own(kit.hero_art(H, M))}
</div></div>

<section class="b-sec" id="research"><div class="wrap">
  <div class="sec-head"><h2>Research</h2></div>
  <p class="lead">{H["statement"]}</p>
  <ul class="topics">{tiles}</ul>
</div></section>

<div class="b-lensed" data-lensed>
{lens_bar(fix)}
{pubs_html}

{articles_html}

{projects_html}

{worlds_html}
</div>

<section class="b-sec b-contact" id="contact"><div class="wrap">
  <div class="sec-head"><h2>Contact</h2></div>
  <p class="lead">{H["contact_lede"]}</p>
  {kit.contact_list(H, fix)}
</div></section>
</main>
{foot(H, "home", fix)}"""
    return kit.page(D, "home", "David Adeshina Arungbemi", body, SCHEME, mood="default", body_class="b-home")

# ---------------------------------------------------------------- a topic page

def topic(data, M):
    H, t, fix = data["H"], data["topic"], kit.linker("topic")
    S = kit.topic_sections(t)
    mood = f"topic-{t['slug']}"
    tabs = "".join(f'<a class="tab" href="{attr(fix("/" + o["slug"] + "/"))}" data-mood="topic-{o["slug"]}">{esc(o["title"])}</a>' for o in S["others"])

    def part(title, ps, cls=""):
        return sec(None, title, cards(ps, M, fix, 3, cls)) if ps else ""
    images = ""
    if S["images"]:
        images = sec(None, "Images", '<div class="wall">' + "".join(world(p, M, fix) for p in S["images"]) + "</div>" + more([("All of Worlds →", "/images.html")]))
    body = f"""{top(H, "topic", fix, "Research")}
<main id="main">
<section class="b-band"><div class="wrap">
  <p class="kicker">Research topic</p>
  <h1>{esc(t["title"])}</h1>
  <p class="statement">{esc(t["statement"])}</p>
  <nav class="tabs" aria-label="Other topics"><span class="tabs-label" aria-hidden="true">Other topics</span>{tabs}</nav>
</div></section>
{part("Start with", S["start"], " is-start")}
{part("Publications", S["pubs"])}{part("Experiments", S["experiments"])}{part("Projects", S["projects"])}{part("Essays", S["essays"])}{images}
</main>
{foot(H, "topic", fix)}"""
    return kit.page(D, "topic", f"{t['title']} · David Adeshina Arungbemi", body, SCHEME, mood=mood, body_class="b-topic")

# ---------------------------------------------------------------- an article

def article(data, M):
    H, A, fix = data["H"], data["article"], kit.linker("article")
    slugs = c._topics_of("article", A["slug"])
    mood = f"topic-{slugs[0]}" if slugs else "default"
    strip = ""
    if slugs:
        links = "".join(f'<a class="tab" href="{attr(fix("/" + s + "/"))}" data-mood="topic-{s}">{esc(c.TOPIC[s]["title"])}</a>' for s in slugs)
        strip = f'<nav class="b-strip" aria-label="Topics of this article"><div class="wrap"><span class="tabs-label" aria-hidden="true">Topics</span>{links}</div></nav>'
    cover = A["cover"]
    cover_html = ""
    if cover:
        cover_html = (f'<figure class="post-cover" data-mood="{M.of(cover["src"])}"><img src="{attr(cover["src"])}" alt="" width="{cover["w"]}" height="{cover["h"]}"></figure>')
    deck = f'<p class="post-deck">{A["deck"]}</p>' if A["deck"] else ""
    body_html = kit.article_body(A, M, room=False)
    body_html = re.sub(r'(<figure[^>]*?) data-peek="', r'\1 data-mood="', body_html)
    near = "".join(f'<a class="near" href="{attr(fix(n["href"]))}" data-own="{M.of(n["img"])}"><img src="{attr(c.smaller(n["img"]))}" alt="" loading="lazy" width="96" height="96">'
                   f'<span><span class="item-kind">{n["label"]}</span><span class="near-title">{n["title"]}</span></span></a>' for n in A["near"])
    body = f"""{top(H, "article", fix, "Articles")}
{strip}
<main id="main" class="post">
<article>
  <header class="post-head"><div class="post-wrap">
    <p class="post-kicker">{kit.relink(A["kicker"], fix)}</p>
    <h1>{A["h1"]}</h1>{deck}
    <p class="post-byline">{A["byline"]}</p>
  </div></header>
  {cover_html}
  <div class="post-body">
{body_html}
    <p class="post-end"><img src="/assets/img/seal-64.png" alt="" width="30" height="30"></p>
  </div>
  <footer class="post-foot">
    <p class="post-origin">{A["origin"]}</p>
    <nav class="nears" aria-label="More articles">{near}</nav>
    {more([("All articles →", "/articles/")])}
  </footer>
</article>
</main>
{foot(H, "article", fix)}"""
    return kit.page(D, "article", f"{A['post']['title']} · Suzume", body, SCHEME, mood=mood, body_class="b-article")

def build(data):
    M = kit.Moods()
    out = kit.OUT / D
    kit.write(out / "index.html", home(data, M))
    kit.write(out / f"{kit.TOPIC}.html", topic(data, M))
    kit.write(out / f"{kit.ARTICLE}.html", article(data, M))
    kit.write(out / "moods.css", "/* Generated by _directions/build.py from his pictures. Every text pair is checked for AA. */\n" + M.css(SCHEME))
    return M
