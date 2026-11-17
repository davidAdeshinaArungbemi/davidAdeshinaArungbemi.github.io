"""Direction C, "Rooms": a walk through his work, one room for each part of it.

The page changes colour as you move from room to room, light or dark, as his own words about the manga
March Comes in Like a Lion have it: "the world and the feelings of the characters seem to move together."
Each room takes its colours from its first picture: a mostly light picture gives the light palette and a
mostly dark one the dark palette, so the page passes through light and dark as you walk. People whose
device is set to dark get every room dark, still coloured by its picture. There is no top bar and no dock:
his name stays at the top left and a short map of the rooms stays at the right edge (a Menu button on
phones and on the article).
"""
import re
import kit, moods, content as c
from kit import esc, attr

D = "c"
LIGHT = 0.55                                                    # a picture lighter than this gives a light room

def scheme_of(a): return "light" if a["light"] > LIGHT else "dark"

# ---------------------------------------------------------------- moods.css: each mood in its own scheme

def moods_css(M, first):
    """Every mood as a checked palette. A mood wears the light or dark palette its picture suggests;
    a device set to dark gets the dark palette for every mood."""
    def block(a, scheme, name):
        t = moods.palette(a, scheme)
        moods.check(t, f"{name} ({scheme})")
        return "".join(f"--{k}:{v};" for k, v in t.items()) + f"color-scheme:{scheme}"
    def sel(name):                                              # the page, and the research doors that carry their own mood
        s = f':root[data-mood="{name}"]'
        if name.startswith("topic-"):
            s += f',.topic[data-mood="{name}"]'
        return s
    out = [f":root{{{block(M.seen[first], scheme_of(M.seen[first]), first)}}}"]
    out += [f"{sel(n)}{{{block(a, scheme_of(a), n)}}}" for n, a in M.seen.items()]
    dark = [f":root{{{block(M.seen[first], 'dark', first)}}}"]
    dark += [f"{sel(n)}{{{block(a, 'dark', n)}}}" for n, a in M.seen.items()]
    out.append("@media (prefers-color-scheme:dark){\n" + "\n".join(dark) + "\n}")
    return "\n".join(out) + "\n"

# ---------------------------------------------------------------- the name and the map

HEAD_JS = "<script>document.documentElement.classList.add('js');/*SCHEMES*/</script>"

def top(fix, progress=False):
    bar = '<div class="c-progress" aria-hidden="true"></div>' if progress else ""
    return f'<header class="c-top">{bar}<a class="c-name" href="{attr(fix("/"))}">David Adeshina Arungbemi</a></header>'

def site_map(items, current=None, kind="location"):
    """The rooms as a list: fixed at the right edge on wide screens, a Menu button and a popover on narrow ones."""
    def lis():
        out = []
        for label, href in items:
            cur = f' aria-current="{kind}"' if href == current else ""
            cls = ' class="c-cv"' if href.endswith("/cv.html") else ""
            out.append(f'<li{cls}><a href="{attr(href)}"{cur}><span class="c-mark" aria-hidden="true"></span>{esc(label)}</a></li>')
        return "".join(out)
    return (f'<nav class="c-map" aria-label="Sections"><ol>{lis()}</ol></nav>'
            f'<button class="c-menu" type="button" popovertarget="c-sheet">{kit.ICON["menu"]}<span>Menu</span></button>'
            f'<div class="c-sheet" id="c-sheet" popover><nav aria-label="Sections"><ol>{lis()}</ol></nav></div>')

def foot(H, here, fix):
    return (f'<footer class="c-foot"><nav class="foot-nav" aria-label="Site">{kit.nav_links(here, fix)}</nav>'
            f'<p>{H["foot"]}</p></footer>')

# ---------------------------------------------------------------- small pieces

def more(links):
    return '<p class="more">' + "".join(f'<a href="{attr(u)}">{t}</a>' for t, u in links) + "</p>"

def items(ps, M, fix, level=3):
    return '<ol class="items">' + "".join(kit.item(p, M, fix, level) for p in ps) + "</ol>"

def worlds(ps, M, fix):
    """His pictures at their own proportions, in rows where every picture has the same height."""
    rows, cur, total = [], [], 0.0
    for p in ps:
        r = p["w"] / p["h"]
        if cur and total + r > 4.2:
            rows.append((cur, total)); cur, total = [], 0.0
        cur.append((p, r)); total += r
        if total >= 2.4:
            rows.append((cur, total)); cur, total = [], 0.0
    if cur:
        rows.append((cur, total))
    out = []
    for row, total in rows:
        figs = "".join(kit.world(p, M, fix).replace('<figure class="world"', f'<figure class="world" style="--r:{r:.3f}"', 1) for p, r in row)
        out.append(f'<div class="worlds-row" style="--sum:{total:.3f}">{figs}</div>')
    return '<div class="worlds">' + "".join(out) + "</div>"

def feature(sel, label, M, fix):
    ink = " is-ink" if sel.get("ink") else ""
    return (f'<a class="feature{ink}" href="{attr(fix(sel["href"]))}" data-peek="{M.of(sel["img"])}">'
            f'<span class="feature-art"><img src="{attr(sel["img"])}" alt="" width="{sel["w"]}" height="{sel["h"]}" loading="lazy"></span>'
            f'<span class="feature-text"><span class="item-kind">{esc(label)}</span>'
            f'<span class="feature-title">{esc(sel["title"])}</span><span class="feature-line">{esc(sel["line"])}</span></span></a>')

# ---------------------------------------------------------------- the homepage

HOME_MAP = [("Start", "#top"), ("Now", "#now"), ("Research", "#research"), ("Publications", "#publications"),
            ("Articles", "#articles"), ("Projects", "#projects"), ("Worlds", "#worlds"), ("Contact", "#contact"),
            ("CV", "/cv.html")]

def home(data, M):
    H, fix = data["H"], kit.linker("home")
    show, first = kit.showcase(M, fix, colour="page")
    sel = data["selected"]
    pubs = H["pubs"]
    m_now, m_research = M.of(H["art"]["src"]), "default"
    m_pubs, m_art = M.of(pubs[0]["img"]), M.of(sel["img"])
    m_proj, m_worlds = M.of(data["projects"][0]["img"]), M.of(data["worlds"][0]["img"])
    body = f"""{top(fix)}
{site_map(HOME_MAP, "#top")}
<main id="main">
<section class="room room-start" id="top" data-room="{first}">
  <div class="room-in start-grid">
    <div class="start-panel">
      <p class="kicker">{kit.relink(H["kicker"], fix)}</p>
      <h1>{H["h1"]}</h1>
      <p class="deck">{H["deck"]}</p>
    </div>
    {show}
  </div>
</section>

<section class="room room-now" id="now" data-room="{m_now}" aria-label="Now">
  <div class="room-in now-grid">
    {kit.now_list(H, fix)}
    {kit.hero_art(H, M)}
  </div>
</section>

<section class="room room-research" id="research" data-room="{m_research}">
  <div class="room-in">
    <h2 class="room-title">Research</h2>
    <p class="statement">{H["statement"]}</p>
    <ul class="doors">{"".join(kit.topic_tile(t, M, fix) for t in c.TOPICS)}</ul>
  </div>
</section>

<section class="room room-pubs" id="publications" data-room="{m_pubs}">
  <div class="room-in">
    <h2 class="room-title">Publications</h2>
    <ol class="pubs">{"".join(kit.pub(p, M, fix) for p in pubs)}</ol>
  </div>
</section>

<section class="room room-articles" id="articles" data-room="{m_art}">
  <div class="room-in">
    <h2 class="room-title">Articles</h2>
    {kit.suzume_note(H, fix)}
    {feature(sel, H["selected"]["label"], M, fix)}
    <div class="cols">
      <div class="col-a"><h3>Experiments</h3>{items(data["experiments"], M, fix, 4)}</div>
      <div class="col-b"><h3>Essays</h3>{items(data["essays"], M, fix, 4)}</div>
    </div>
    {more([("All articles →", "/articles/"), ("Suzume on Medium →", c.MEDIUM)])}
  </div>
</section>

<section class="room room-projects" id="projects" data-room="{m_proj}">
  <div class="room-in">
    <h2 class="room-title">Projects</h2>
    {items(data["projects"], M, fix, 3).replace('class="items"', 'class="items items-wide"', 1)}
    {more([(H["all_projects"], "/projects/"), ("GitHub as Suzume →", "https://github.com/suzume-hue"), ("GitHub as David →", "https://github.com/davidAdeshinaArungbemi")])}
  </div>
</section>

<section class="room room-worlds" id="worlds" data-room="{m_worlds}">
  <div class="room-in">
    <h2 class="room-title">Worlds</h2>
    <p class="statement">{H["worlds_intro"]}</p>
    {worlds(data["worlds"], M, fix)}
    {more([(H["worlds_all"], "/images.html")])}
  </div>
</section>

<section class="room room-contact" id="contact" data-room="default">
  <div class="room-in">
    <h2 class="room-title">Contact</h2>
    <p class="contact-lede">{H["contact_lede"]}</p>
    {kit.contact_list(H, fix)}
  </div>
</section>
</main>
{foot(H, "home", fix)}"""
    return kit.page(D, "home", "David Adeshina Arungbemi", body, "light", mood=first, extra_head=HEAD_JS, body_class="c-home"), first

# ---------------------------------------------------------------- the topic page

def topic(data, M):
    H, t, fix = data["H"], data["topic"], kit.linker("topic")
    S = kit.topic_sections(t)
    mood = f"topic-{t['slug']}"
    rooms, map_items = [], [(t["title"], "#top")]

    def room(rid, label, title, inner, ps):
        m = M.of(ps[0]["img"])
        rooms.append(f'<section class="room" id="{rid}" data-room="{m}"><div class="room-in"><h2 class="room-title">{title}</h2>{inner}</div></section>')
        map_items.append((label, f"#{rid}"))

    if S["start"]:
        room("start-with", "Start with", "Start with", items(S["start"], M, fix, 3).replace('class="items"', 'class="items items-start"', 1), S["start"])
    if S["pubs"]:
        room("publications", "Publications", "Publications", items(S["pubs"], M, fix, 3), S["pubs"])
    if S["experiments"]:
        room("experiments", "Experiments", "Experiments", items(S["experiments"], M, fix, 3).replace('class="items"', 'class="items items-wide"', 1), S["experiments"])
    if S["projects"]:
        room("projects", "Projects", "Projects", items(S["projects"], M, fix, 3).replace('class="items"', 'class="items items-wide"', 1), S["projects"])
    if S["essays"]:
        room("essays", "Essays", "Essays", items(S["essays"], M, fix, 3).replace('class="items"', 'class="items items-wide"', 1), S["essays"])
    if S["images"]:
        room("images", "Images", "Images", worlds(S["images"], M, fix) + more([("All of Worlds →", "/images.html")]), S["images"])
    others = f'<ul class="doors doors-3">{"".join(kit.topic_tile(o, M, fix) for o in S["others"])}</ul>'
    rooms.append(f'<section class="room" id="other-topics" data-room="default"><div class="room-in"><h2 class="room-title">Other topics</h2>{others}</div></section>')
    map_items += [("Other topics", "#other-topics"), ("CV", "/cv.html")]

    body = f"""{top(fix)}
{site_map(map_items, "#top")}
<main id="main">
<section class="room room-topic" id="top" data-room="{mood}">
  <div class="room-in">
    <p class="kicker">Research topic</p>
    <h1>{esc(t["title"])}</h1>
    <p class="statement">{esc(t["statement"])}</p>
  </div>
</section>
{"".join(rooms)}
</main>
{foot(H, "topic", fix)}"""
    return kit.page(D, "topic", f"{t['title']} · David Adeshina Arungbemi", body, "light", mood=mood, extra_head=HEAD_JS, body_class="c-topic")

# ---------------------------------------------------------------- the article

def article(data, M):
    H, A, fix = data["H"], data["article"], kit.linker("article")
    cover = A["cover"]
    mood = M.of(cover["src"]) if cover else "default"
    art = (f'<figure class="cover-art"><img src="{attr(cover["src"])}" alt="" width="{cover["w"]}" height="{cover["h"]}" fetchpriority="high"></figure>') if cover else ""
    deck = f'<p class="post-deck">{A["deck"]}</p>' if A["deck"] else ""
    near = "".join(f'<a class="near" href="{attr(fix(n["href"]))}" data-peek="{M.of(n["img"])}"><img src="{attr(c.smaller(n["img"]))}" alt="" loading="lazy" width="96" height="96">'
                   f'<span><span class="item-kind">{n["label"]}</span><span class="near-title">{n["title"]}</span></span></a>' for n in A["near"])
    nav = [(t, fix(u)) for t, u in kit.NAV]
    here = next(u for t, u in nav if t == "Articles")
    body = f"""{top(fix, progress=True)}
{site_map(nav, here, "page")}
<main id="main" class="post">
<article>
  <header class="room cover" id="top" data-room="{mood}">
    {art}
    <div class="cover-text">
      <p class="kicker">{kit.relink(A["kicker"], fix)}</p>
      <h1>{A["h1"]}</h1>{deck}
      <p class="byline">{A["byline"]}</p>
    </div>
  </header>
  <div class="post-body">
{kit.article_body(A, M).replace('sizes="(min-width: 940px) 900px, 100vw"', 'sizes="100vw"')}
    <p class="post-end"><img src="/assets/img/seal-64.png" alt="" width="30" height="30" loading="lazy"></p>
  </div>
  <footer class="post-foot">
    <p class="origin">{A["origin"]}</p>
    <nav class="nears" aria-label="More articles">{near}</nav>
    {more([("All articles →", "/articles/")])}
  </footer>
</article>
</main>
{foot(H, "article", fix)}"""
    return kit.page(D, "article", f"{A['post']['title']} · Suzume", body, "light", mood=mood, extra_head=HEAD_JS, body_class="c-article")

# ---------------------------------------------------------------- build

def build(data):
    M = kit.Moods()
    out = kit.OUT / D
    index, first = home(data, M)
    pages = [index, topic(data, M), article(data, M)]
    import json
    lite = {n: scheme_of(a) for n, a in M.seen.items()}
    inject = "window.cSchemes=" + json.dumps(lite) + ";"
    pages = [pg.replace("/*SCHEMES*/", inject).replace('<img src="/assets/img/seal.png"', '<img loading="lazy" src="/assets/img/seal.png"') for pg in pages]
    # In C the page follows the rooms. Pointing at a piece doesn't recolour the page (a dark picture in a light
    # room would flip the whole page); only the four topic doors lend their colours.
    pages = [re.sub(r'<(?!li class="topic")([^>]*?) data-peek="[^"]*"', r'<\1', pg) for pg in pages]
    kit.write(out / "index.html", pages[0])
    kit.write(out / f"{kit.TOPIC}.html", pages[1])
    kit.write(out / f"{kit.ARTICLE}.html", pages[2])
    kit.write(out / "moods.css", "/* Generated by _directions/build.py from his pictures. Each mood is in the light or dark palette its picture suggests; every text pair is checked for AA. */\n" + moods_css(M, first))
    return M
