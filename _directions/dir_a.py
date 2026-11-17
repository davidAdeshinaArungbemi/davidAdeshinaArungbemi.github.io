"""Direction A, "The screen": a dim room lit by whatever is showing.

The homepage opens on a screen that plays his clips one after another, and the room takes its light
from the clip: ground, glow and the colour of links and controls. Pointing at or focusing any piece
makes that piece the light for a moment. Getting around is a dock that stays at the bottom of the screen.
"""
import kit, moods, content as c
from kit import esc, attr

D, SCHEME = "a", "dark"

def mix(a, b, t):
    """sRGB blend of two hex colours, as a CSS gradient blends them."""
    return "#" + "".join(f"{round(int(a[i:i+2], 16) * (1 - t) + int(b[i:i+2], 16) * t):02X}" for i in (1, 3, 5))

def tune(t, a, scheme):
    """Add the room light: the brightest (or in daylight, deepest) the ground may get behind text.
    It never passes ground-3, which every text colour is already checked against."""
    limit = moods.luminance(t["ground-3"])
    for name, glow in (("veil", t["glow"]), ("veil-2", t["glow-2"])):
        alpha = 0.6
        while alpha > 0:
            v = mix(t["ground"], glow, alpha)
            ok = moods.luminance(v) <= limit if scheme == "dark" else moods.luminance(v) >= limit
            if ok and all(moods.contrast(t[k], v) >= 4.6 for k in ("ink-2", "accent", "accent-2")): break
            alpha -= 0.02
        t[name] = mix(t["ground"], glow, max(alpha, 0))
    return t

def top(H, fix):
    return (f'<header class="a-head"><a class="a-name" href="{fix("/")}">David Adeshina Arungbemi</a>'
            f'<span class="a-also">{kit.also_suzume(H, fix)}</span>'
            f'<button class="icon-btn" type="button" data-scheme-toggle aria-label="Switch between light and dark">{kit.ICON["scheme"]}</button></header>')

def dock(here, fix, current=None):
    items = kit.HOME_NAV if here == "home" else kit.NAV
    main = {"Research", "Publications", "CV"}                   # the ones a phone keeps in the bar
    links = "".join(f'<a href="{attr(fix(u))}"' + ("" if t in main else ' class="dock-more"') + (' aria-current="page"' if t == current else "") + f">{t}</a>"
                    for t, u in items)
    sheet = "".join(f'<a href="{attr(fix(u))}">{t}</a>' for t, u in items)
    return (f'<nav class="a-dock" aria-label="Sections">{links}'
            f'<button class="dock-menu" type="button" popovertarget="a-menu">Menu</button></nav>'
            f'<div class="a-menu" id="a-menu" popover><nav aria-label="All sections">{sheet}</nav></div>')

def foot(H, here, fix):
    return (f'<footer class="a-foot"><nav class="foot-nav" aria-label="Site">{kit.nav_links(here, fix)}</nav>'
            f'<p>{H["foot"]}</p></footer>')

def items(ps, M, fix, cls="", level=3):
    return f'<ol class="items{cls}">' + "".join(kit.item(p, M, fix, level) for p in ps) + "</ol>"

def more(links):
    return '<p class="more">' + "".join(f'<a href="{attr(u)}">{t}</a>' for t, u in links) + "</p>"

def home(data, M):
    H, fix = data["H"], kit.linker("home")
    show, first = kit.showcase(M, fix, colour="page", ambient=True)
    sel = data["selected"]
    body = f"""<div class="a-glow" aria-hidden="true"></div>
{top(H, fix)}
{dock("home", fix)}
<main id="main">
<section class="a-hero" id="top">
  <div class="a-hero-text">
    <h1>{H["h1"]}</h1>
    <p class="a-deck">{H["deck"]}</p>
  </div>
  {show}
</section>

<section class="a-sec a-about">
  {kit.now_list(H, fix)}
  {kit.hero_art(H, M)}
</section>

<section class="a-sec" id="research">
  <h2>Research</h2>
  <p class="lead">{H["statement"]}</p>
  <ul class="topics">{"".join(kit.topic_tile(t, M, fix) for t in c.TOPICS)}</ul>
</section>

<section class="a-sec" id="publications">
  <h2>Publications</h2>
  <ol class="pubs">{"".join(kit.pub(p, M, fix) for p in H["pubs"])}</ol>
</section>

<section class="a-sec" id="articles">
  <h2>Articles</h2>
  {kit.suzume_note(H, fix)}
  <a class="feature{' is-ink' if sel.get('ink') else ''}" href="{attr(fix(sel['href']))}" data-peek="{M.of(sel['img'])}">
    <span class="feature-art"><img src="{attr(sel['img'])}" alt="" width="{sel['w']}" height="{sel['h']}" loading="lazy"></span>
    <span class="feature-text"><span class="item-kind">{esc(H['selected']['label'])}</span>
    <span class="feature-title">{esc(sel['title'])}</span><span class="feature-line">{esc(sel['line'])}</span></span>
  </a>
  <h3>Experiments</h3>
  {items(data["experiments"], M, fix, level=4)}
  <h3>Essays</h3>
  {items(data["essays"], M, fix, level=4)}
  {more([("All articles →", "/articles/"), ("Suzume on Medium →", c.MEDIUM)])}
</section>

<section class="a-sec" id="projects">
  <h2>Projects</h2>
  {items(data["projects"], M, fix)}
  {more([(H["all_projects"], "/projects/"), ("GitHub as Suzume →", "https://github.com/suzume-hue"), ("GitHub as David →", "https://github.com/davidAdeshinaArungbemi")])}
</section>

<section class="a-sec" id="worlds">
  <h2>Worlds</h2>
  <p class="lead">{H["worlds_intro"]}</p>
  <div class="wall">{"".join(kit.world(p, M, fix) for p in data["worlds"])}</div>
  {more([(H["worlds_all"], "/images.html")])}
</section>

<section class="a-sec" id="contact">
  <h2>Contact</h2>
  <p class="lead">{H["contact_lede"]}</p>
  {kit.contact_list(H, fix)}
</section>
</main>
{foot(H, "home", fix)}"""
    return kit.page(D, "home", "David Adeshina Arungbemi", body, SCHEME, mood=first)

def topic(data, M):
    H, t, fix = data["H"], data["topic"], kit.linker("topic")
    S = kit.topic_sections(t)
    mood = f"topic-{t['slug']}"
    others = "".join(f'<a class="chip" href="{attr(fix("/" + o["slug"] + "/"))}" data-mood="topic-{o["slug"]}" data-peek="topic-{o["slug"]}">{esc(o["title"])}</a>' for o in S["others"])
    def sec(title, ps, cls=""):
        return f'<section class="a-sec"><h2>{title}</h2>{items(ps, M, fix, cls)}</section>' if ps else ""
    tiles = "".join(f'<li data-peek="{M.of(p["img"])}"><a href="{attr(p["href"])}"><img src="{attr(p["img"])}" alt="{attr(p["alt"])}" loading="lazy" width="{p["w"]}" height="{p["h"]}"><span>{esc(p["title"])}</span></a></li>' for p in S["images"])
    images = (f'<section class="a-sec"><h2>Images</h2><ul class="tiles">{tiles}</ul>{more([("All of Worlds →", "/images.html")])}</section>') if S["images"] else ""
    body = f"""<div class="a-glow" aria-hidden="true"></div>
{top(H, fix)}
{dock("topic", fix, "Research")}
<main id="main">
<section class="a-page-head">
  <p class="kicker">Research topic</p>
  <h1>{esc(t["title"])}</h1>
  <p class="statement">{esc(t["statement"])}</p>
  <p class="others"><span>Other topics:</span> {others}</p>
</section>
<section class="a-sec"><h2>Start with</h2>{items(S["start"], M, fix, " is-start")}</section>
{sec("Publications", S["pubs"])}{sec("Experiments", S["experiments"])}{sec("Projects", S["projects"])}{sec("Essays", S["essays"])}{images}
</main>
{foot(H, "topic", fix)}"""
    return kit.page(D, "topic", f"{t['title']} · David Adeshina Arungbemi", body, SCHEME, mood=mood)

def article(data, M):
    H, A, fix = data["H"], data["article"], kit.linker("article")
    cover = A["cover"]
    mood = M.of(cover["src"]) if cover else "default"
    cover_html = (f'<figure class="post-cover" data-room="{mood}"><img src="{attr(cover["src"])}" alt="" width="{cover["w"]}" height="{cover["h"]}"></figure>') if cover else ""
    deck = f'<p class="post-deck">{A["deck"]}</p>' if A["deck"] else ""
    near = "".join(f'<a class="near" href="{attr(fix(n["href"]))}" data-peek="{M.of(n["img"])}"><img src="{attr(c.smaller(n["img"]))}" alt="" loading="lazy" width="96" height="96">'
                   f'<span><span class="item-kind">{n["label"]}</span><span class="near-title">{n["title"]}</span></span></a>' for n in A["near"])
    body = f"""<div class="a-glow" aria-hidden="true"></div>
<div class="read-progress" aria-hidden="true"></div>
{top(H, fix)}
{dock("article", fix, "Articles")}
<main id="main" class="post">
<article>
  <header class="post-head">
    <p class="kicker">{kit.relink(A["kicker"], fix)}</p>
    <h1>{A["h1"]}</h1>{deck}
    <p class="byline">{A["byline"]}</p>
  </header>
  {cover_html}
  <div class="post-body">
{kit.article_body(A, M)}
    <p class="post-end"><img src="/assets/img/seal-64.png" alt="" width="30" height="30"></p>
  </div>
  <footer class="post-foot">
    <p class="origin">{A["origin"]}</p>
    <nav class="nears" aria-label="More articles">{near}</nav>
    {more([("All articles →", "/articles/")])}
  </footer>
</article>
</main>
{foot(H, "article", fix)}"""
    return kit.page(D, "article", f"{A['post']['title']} · Suzume", body, SCHEME, mood=mood)

def build(data):
    M = kit.Moods()
    out = kit.OUT / D
    kit.write(out / "index.html", home(data, M))
    kit.write(out / f"{kit.TOPIC}.html", topic(data, M))
    kit.write(out / f"{kit.ARTICLE}.html", article(data, M))
    kit.write(out / "moods.css", "/* Generated by _directions/build.py from his pictures. Every text pair is checked for AA. */\n" + M.css(SCHEME, tune))
    return M
