"""Direction D, A and B mixed: B's way through the work, inside A's room.

From B: the four topics as colour fields, the topic bar that recolours the page and brings that topic's work
forward in every section, cards with the picture on top, and counts. From A: the dark room with its soft light,
the curves, and the lit screen for the clips.

Who sets the colour:
- at the top, the clip that is playing lights the room (the hero is a data-room that the showcase recolours);
- below it, the chosen topic does (the rest of the page is one data-room whose mood the topic bar sets);
- a card pointed at or focused takes its own picture's colours (data-own), without changing the page.
"""
import kit, content as c
from kit import esc, attr
import dir_a
from dir_b import own, no_peek, item, pub, world, cards, more, feature, sec, lens_bar, GITHUB_SUZUME, GITHUB_DAVID

D, SCHEME = "d", "dark"

# ---------------------------------------------------------------- page furniture

def top(H, here, fix, current=None):
    return (f'<header class="d-head"><div class="wrap d-head-row">'
            f'<a class="d-name" href="{attr(fix("/"))}">David Adeshina Arungbemi</a>'
            f'<span class="d-also">{kit.also_suzume(H, fix)}</span>'
            f'<nav class="d-nav" aria-label="Sections">{kit.nav_links(here, fix, current)}</nav>'
            f'<button class="icon-btn" type="button" data-scheme-toggle aria-label="Switch between light and dark">{kit.ICON["scheme"]}</button>'
            f'</div></header>')

def foot(H, here, fix):
    back = "" if here == "home" else f' <a href="{attr(fix("/"))}">Back to the site →</a>'
    return (f'<footer class="d-foot"><div class="wrap"><nav class="foot-nav" aria-label="Site">{kit.nav_links(here, fix)}</nav>'
            f'<p>{H["foot"]}{back}</p></div></footer>')

GLOW = '<div class="d-glow" aria-hidden="true"></div>'

# ---------------------------------------------------------------- the homepage

def home(data, M):
    H, fix = data["H"], kit.linker("home")
    show, first = kit.showcase(M, fix, colour="page", ambient=True)
    sel_key = H["selected"]["slug"]
    sel = data["selected"]

    # every piece the topic bar can bring forward; the ones with data-home are the homepage's own selection
    home_art = set(H["home_articles"])
    exp = [p for p in data["all_articles"] if p["key"] != sel_key and p["group"] == "experiment"]
    ess = [p for p in data["all_articles"] if p["key"] != sel_key and p["group"] != "experiment"]
    art_home = {p["id"] for p in data["all_articles"] if p["key"] in home_art}
    first_proj = {k: i for i, k in enumerate(H["home_projects"])}
    projects = sorted(data["all_projects"], key=lambda p: first_proj.get(p["key"], 99))
    proj_home = {p["id"] for p in projects if p["key"] in first_proj}
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

    body = f"""{GLOW}
{top(H, "home", fix)}
<main id="main">
<section class="d-hero" id="top" data-room="{first}"><div class="wrap d-hero-grid">
  <div class="d-hero-text">
    <h1>{H["h1"]}</h1>
    <p class="d-deck">{H["deck"]}</p>
  </div>
  {show}
</div></section>

<div class="d-work" data-room="default" data-lens-room>
<div class="d-now"><div class="wrap"><div class="d-now-card">
  {kit.now_list(H, fix)}
  {own(kit.hero_art(H, M))}
</div></div></div>

<section class="b-sec" id="research"><div class="wrap">
  <div class="sec-head"><h2>Research</h2></div>
  <p class="lead">{H["statement"]}</p>
  <ul class="topics">{tiles}</ul>
</div></section>

<div class="d-lensed" data-lensed>
{lens_bar(fix).replace('<p class="visually-hidden" role="status"', '<p class="lens-cv"><a href="/cv.html">CV</a></p><p class="visually-hidden" role="status"', 1)}
{pubs_html}

{articles_html}

{projects_html}

{worlds_html}
</div>

<section class="b-sec d-contact" id="contact"><div class="wrap">
  <div class="sec-head"><h2>Contact</h2></div>
  <p class="lead">{H["contact_lede"]}</p>
  {kit.contact_list(H, fix)}
</div></section>
</div>
</main>
{foot(H, "home", fix)}"""
    return kit.page(D, "home", "David Adeshina Arungbemi", body, SCHEME, mood=first, body_class="d-home")

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
    body = f"""{GLOW}
{top(H, "topic", fix, "Research")}
<main id="main">
<section class="d-band-wrap"><div class="wrap"><div class="d-band">
  <p class="kicker">Research topic</p>
  <h1>{esc(t["title"])}</h1>
  <p class="statement">{esc(t["statement"])}</p>
  <nav class="tabs" aria-label="Other topics"><span class="tabs-label" aria-hidden="true">Other topics</span>{tabs}</nav>
</div></div></section>
{part("Start with", S["start"], " is-start")}
{part("Publications", S["pubs"])}{part("Experiments", S["experiments"])}{part("Projects", S["projects"])}{part("Essays", S["essays"])}{images}
</main>
{foot(H, "topic", fix)}"""
    return kit.page(D, "topic", f"{t['title']} · David Adeshina Arungbemi", body, SCHEME, mood=mood, body_class="d-topic")

# ---------------------------------------------------------------- an article

def article(data, M):
    import re
    H, A, fix = data["H"], data["article"], kit.linker("article")
    slugs = c._topics_of("article", A["slug"])
    mood = f"topic-{slugs[0]}" if slugs else "default"
    strip = ""
    if slugs:
        links = "".join(f'<a class="tab" href="{attr(fix("/" + s + "/"))}" data-mood="topic-{s}">{esc(c.TOPIC[s]["title"])}</a>' for s in slugs)
        strip = f'<nav class="d-strip" aria-label="Topics of this article"><div class="post-wrap"><span class="tabs-label" aria-hidden="true">Topics</span>{links}</div></nav>'
    cover = A["cover"]
    cover_html = ""
    if cover:
        cover_html = (f'<figure class="post-cover" data-mood="{M.of(cover["src"])}"><img src="{attr(cover["src"])}" alt="" width="{cover["w"]}" height="{cover["h"]}"></figure>')
    deck = f'<p class="post-deck">{A["deck"]}</p>' if A["deck"] else ""
    body_html = kit.article_body(A, M, room=False)
    body_html = re.sub(r'(<figure[^>]*?) data-peek="', r'\1 data-mood="', body_html)
    near = "".join(f'<a class="near" href="{attr(fix(n["href"]))}" data-own="{M.of(n["img"])}"><img src="{attr(c.smaller(n["img"]))}" alt="" loading="lazy" width="96" height="96">'
                   f'<span><span class="item-kind">{n["label"]}</span><span class="near-title">{n["title"]}</span></span></a>' for n in A["near"])
    body = f"""{GLOW}
<div class="read-progress" aria-hidden="true"></div>
{top(H, "article", fix, "Articles")}
<main id="main" class="post">
<article>
  <header class="post-head"><div class="post-wrap">
    <p class="post-kicker">{kit.relink(A["kicker"], fix)}</p>
    <h1>{A["h1"]}</h1>{deck}
    <p class="post-byline">{A["byline"]}</p>
  </div></header>
  {strip}
  {cover_html}
  <div class="post-body">
{body_html}
    <p class="post-end"><img src="/assets/img/seal-64.png" alt="" width="30" height="30" loading="lazy"></p>
  </div>
  <footer class="post-foot">
    <p class="post-origin">{A["origin"]}</p>
    <nav class="nears" aria-label="More articles">{near}</nav>
    {more([("All articles →", "/articles/")])}
  </footer>
</article>
</main>
{foot(H, "article", fix)}"""
    return kit.page(D, "article", f"{A['post']['title']} · Suzume", body, SCHEME, mood=mood, body_class="d-article")

def listed(page):
    """Lists styled without bullets lose their list role in Safari; say it outright."""
    for tag in ('<ol class="cards', '<ul class="topics"', '<ul class="contact-list"', '<ol class="showcase-picks"'):
        page = page.replace(tag, tag[:3] + ' role="list"' + tag[3:])
    return page

def build(data):
    M = kit.Moods()
    out = kit.OUT / D
    kit.write(out / "index.html", listed(home(data, M)))
    kit.write(out / f"{kit.TOPIC}.html", listed(topic(data, M)))
    kit.write(out / f"{kit.ARTICLE}.html", listed(article(data, M)))
    kit.write(out / "moods.css", "/* Generated by _directions/build.py from his pictures. Every text pair is checked for AA. */\n" + M.css(SCHEME, dir_a.tune))
    return M
