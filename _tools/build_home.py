"""The homepage (index.html), written whole from the lists the other build scripts keep, plus its own words below.

Every build script runs this at the end (design.finish()), so the homepage is always current. To run it alone:
  python3 _tools/build_home.py
It keeps index.html's own title, description, link-preview and JSON-LD lines exactly as they are
(design.keep_meta), so edit those in index.html by hand if they ever need to change.

Top to bottom: the opening (his line, the deck, and the screen that plays the clips; the screen's colours light the
room while you're up there), Now, Research (the statement and the four topics as fields of colour), then a topic
bar over Publications, Articles, Projects and Worlds (choosing a topic lights the rest of the page in its colours
and shows every piece in it, with counts), and Contact. Every piece is in the page: the ones marked data-home are
the homepage's own selection, shown under "All"; the rest show only under their topics.
"""
from pathlib import Path
import design
from design import esc, attr
import build_cards, build_gallery, build_topics
from build_blog import load_all, month

# ---------------------------------------------------------------- his words on the homepage
# Moved here unchanged from the hand-written index.html on 17 Nov 2026, when the homepage became fully generated.

# the opening line and the deck under it
H1 = "I follow what moves me, then test whether it's true."

DECK = ("Stories and images let us live other lives and come back changed. I'm curious what the future looks like when people and AI can do that for each "
 'other, and I build small experiments to find out.')

# Now / Before / Looking for: (term, text as HTML)
NOW = [('Now', 'Research fellow at <strong>MARS 5.0</strong>, Cambridge AI Safety Hub: agentic moral alignment research, mentored by Elizaveta Tennant'),
 ('Before',
  'Futurekind Fellowship in AI and animal welfare, where I wrote a <a href="https://doi.org/10.5281/zenodo.21294610">preprint on stories and '
  'speciesism in language models</a>'),
 ('Looking for',
  "A funded PhD, or a funded master's as a first step, starting in 2027; also research internships and fellowships. If you like what I do, <a "
  'href="#contact">get in touch →</a>')]

# the ink head beside Now
ART = {'src': '/assets/img/hero-head.jpg',
 'alt': 'A head in profile drawn entirely from small ink icons — ice-cream cones, pizza slices, mugs, music notes — with one patch at the back of '
        'the head ringed by a dashed red line where the icons have changed colour.',
 'w': 980,
 'h': 1050,
 'caption': 'From a distance, a person. Up close, nothing but choices.<br><span class="credit">Cover sketch for <em>You Are What You Prefer</em> · '
            'ink on paper, Processing · 2026</span>'}

# the publications as the homepage gives them (citation, what it found, links); the topic pages use the shorter build_topics.PUBS
PUBS = [{'href': 'https://doi.org/10.5281/zenodo.21294610',
  'img': '/assets/img/work-stories.jpg',
  'label': 'Preprint · not peer-reviewed · 2026',
  'title': 'Narrative Transportation and Speciesism in Large Language Models',
  'cite': "<strong>D. A. Arungbemi</strong>. Zenodo, 2026. Research done during Electric Sheep's Futurekind Fellowship.",
  'line': 'Can a story make a language model care more about an animal? Five models read a story about an animal, the same facts written plainly, or '
          'nothing, then answered a speciesism questionnaire. On the questions about that animal, their speciesism, already modest, fell to nearly '
          'zero after the story; the plain facts generally did not change it. The effects were small in absolute terms.',
  'links': '<a href="https://doi.org/10.5281/zenodo.21294610">doi:10.5281/zenodo.21294610</a><a '
           'href="https://zenodo.org/records/21294610/files/arungbemi-2026-narrative-transportation-speciesism-llms.pdf">PDF</a>'},
 {'href': 'https://doi.org/10.1109/ACCESS.2025.3602871',
  'img': '/assets/cards/gestures.jpg',
  'label': 'Journal article · peer-reviewed · 2025',
  'title': 'An End to End Wearable Device and System for Indefinite, Continuous, Real Time Gesture Recognition of Directional and Shape-Based Arm '
           'Gestures',
  'cite': '<strong>Co-author</strong>. <em>IEEE Access</em> 13, 153436–153463, 2025.',
  'line': 'A wearable that recognises arm gestures, both directions and drawn shapes, continuously and in real time. I designed its AI, from the raw '
          'motion data to the model that names each gesture, and the interface of the live app: how people experience the system as they use it.',
  'links': '<a href="https://doi.org/10.1109/ACCESS.2025.3602871">doi:10.1109/ACCESS.2025.3602871</a><span>Open access</span>'}]

# the note that opens Articles
SUZUME = ('I publish under my pen name, Suzume (雀, sparrow). If you\'ve read Suzume on Medium or found <a href="https://github.com/suzume-hue">suzume-hue</a> '
 "on GitHub, that's me.")

# the article shown large under Articles; he wants Dream a Better Dream kept here (ask before swapping it)
SELECTED = 'dream-a-better-dream'

SELECTED_LABEL = 'Selected article'

WORLDS_INTRO = "Things that don't exist until someone makes them, in code, in 3D with Blender, and by hand."

CONTACT_LEDE = "If you like what I do — or disagree with any of it — I'd like to hear from you."

# (label, links as HTML)
CONTACT = [('Email', '<a href="mailto:arungbemiADavid@outlook.com">Send me an email →</a>'),
 ('LinkedIn', '<a href="https://www.linkedin.com/in/davidadeshina">linkedin.com/in/davidadeshina</a>'),
 ('GitHub',
  '<a href="https://github.com/davidAdeshinaArungbemi">davidAdeshinaArungbemi</a> &nbsp;·&nbsp; <a '
  'href="https://github.com/suzume-hue">suzume-hue</a>'),
 ('Writing', '<a href="https://suzume1.medium.com/">suzume1.medium.com</a>'),
 ('Papers',
  '<a href="https://doi.org/10.5281/zenodo.21294610">Zenodo</a> &nbsp;·&nbsp; <a href="https://doi.org/10.1109/ACCESS.2025.3602871">IEEE Access</a>'),
 ('Company', '<a href="https://gyronics.com">gyronics.com</a>')]

# ---------------------------------------------------------------- the pieces

TOPICS = build_topics.TOPICS

def topics_of(kind, key):
    return [t["slug"] for t in TOPICS if (kind, key) in set(t["start"]) | set(t["items"])]

def article_card(p, home):
    group = "experiment" if "experiment" in p["kind"].lower() else "essay"
    return design.card(f"/articles/{p['slug']}/", design.smaller(p["cover"]), f"{p['kind']} · {month(p['date'])}", p["title"], p["line"],
                       p.get("tags", ()), group=group, topics=topics_of("article", p["slug"]), home=home, level=4)

def project_card(p, home):
    link, img, kind, title, line, extras = p
    return design.card(link, img, kind, title, line, build_cards.TAGS[title], extras, topics=topics_of("project", title), home=home)

def world_card(it, home):
    slug, title, meta, caption, alt = it
    video = build_gallery.VIDEOS.get(slug)
    return design.world(slug, title, meta, build_gallery.SHORT.get(slug, caption), alt or video[4],
                        poster=("/" + video[1]) if video else None, topics=topics_of("image", slug), home=home)

def pub_card(p):
    key = "preprint" if "zenodo" in p["href"] else "gestures"
    w, h = design.size(p["img"])
    return (f'<li class="pub" data-own="{design.mood_name(p["img"])}" data-topics="{" ".join(topics_of("pub", key))}" data-home>'
            f'<a class="pub-thumb" href="{attr(p["href"])}" tabindex="-1" aria-hidden="true"><img src="{attr(p["img"])}" alt="" width="{w}" height="{h}" loading="lazy"></a>'
            f'<div class="pub-text"><p class="item-kind">{esc(p["label"])}</p>'
            f'<h3 class="pub-title"><a href="{attr(p["href"])}">{p["title"]}</a></h3>'
            f'<p class="pub-cite">{p["cite"]}</p><p class="pub-line">{p["line"]}</p>'
            f'<p class="pub-links">{p["links"]}</p></div></li>')

def lead_picture(t):
    """A topic's picture: its first "start with" piece that isn't an image."""
    posts = {p["slug"]: p for p in load_all()}
    projects = {p[3]: p for p in build_cards.PROJECTS}
    kind, key = next(i for i in t["start"] if i[0] != "image")
    if kind == "pub": return design.absolute(build_topics.PUBS[key][1])
    if kind == "article": return design.smaller(posts[key]["cover"])
    return design.absolute(projects[key][1])

def clips():
    pieces = {it[0]: it for _, _, _, items in build_gallery.GROUPS for it in items}
    out = []
    for slug, src, seconds, own in build_gallery.CLIPS:
        _, title, meta, caption, _ = pieces[slug]
        _, poster, w, h, label = build_gallery.VIDEOS[slug]
        if own: poster, w, h, label = own                 # a clip framed differently from the piece's video
        out.append(dict(slug=slug, title=title, line=build_gallery.SHORT.get(slug, caption), meta=meta, src="/" + src,
                        poster="/" + poster, w=w, h=h, label=label, seconds=seconds))
    return out

def nows():
    return '<dl class="now">' + "".join(f"<div><dt>{dt}</dt><dd>{dd}</dd></div>" for dt, dd in NOW) + "</dl>"

def head_art():
    a = ART
    return (f'<figure class="head-art" data-own="{design.mood_name(a["src"])}"><img src="{attr(a["src"])}" alt="{attr(a["alt"])}" width="{a["w"]}" height="{a["h"]}" loading="lazy">'
            f'<figcaption>{a["caption"]}</figcaption></figure>')

# ---------------------------------------------------------------- the page

def page():
    posts = load_all()
    selected = next(p for p in posts if p["slug"] == SELECTED)
    home_posts = {p["slug"] for p in posts if p.get("home")}
    exp = [p for p in posts if p["slug"] != SELECTED and "experiment" in p["kind"].lower()]
    ess = [p for p in posts if p["slug"] != SELECTED and "experiment" not in p["kind"].lower()]
    first = {k: i for i, k in enumerate(build_cards.HOME)}
    projects = sorted(build_cards.PROJECTS, key=lambda p: first.get(p[3], 99))
    pieces = [it for _, _, _, items in build_gallery.GROUPS for it in items]
    by_slug = {it[0]: it for it in pieces}
    shown = list(build_gallery.SHOWCASE)
    extra = []
    for t in TOPICS:
        for kind, key in list(t["start"]) + [i for i in t["items"] if i not in t["start"]]:
            if kind == "image" and key not in shown and key not in extra:
                extra.append(key)

    show = design.showcase(clips())
    first_mood = design.mood_name(clips()[0]["poster"])
    tiles = "".join(design.topic_tile(t["slug"], t["title"], t["line"], len(set(t["start"]) | set(t["items"])), lead_picture(t)) for t in TOPICS)
    sel_img = design.smaller(selected["cover"])
    feature = design.feature(f"/articles/{SELECTED}/", sel_img, f"{SELECTED_LABEL} · {month(selected['date'])}", selected["title"],
                             selected["line"], selected.get("tags", ()), topics=topics_of("article", SELECTED), ink=bool(selected.get("ink")))

    pubs = design.section("publications", "Publications", f'<ol class="cards pubs">{"".join(pub_card(p) for p in PUBS)}</ol>', lensed=True)
    articles = design.section("articles", "Articles",
        f'<div class="suzume" id="suzume"><img src="/assets/img/seal.png" alt="" width="40" height="39"><p>{SUZUME}</p></div>'
        + feature
        + f'<div class="group" data-lens-group><h3 class="group-title">Experiments</h3>{design.cards([article_card(p, p["slug"] in home_posts) for p in exp])}</div>'
        + f'<div class="group" data-lens-group><h3 class="group-title">Essays</h3>{design.cards([article_card(p, p["slug"] in home_posts) for p in ess])}</div>'
        + design.more([("All articles →", "/articles/"), ("Suzume on Medium →", design.MEDIUM)]), lensed=True)
    projects_html = design.section("projects", "Projects",
        design.cards([project_card(p, p[3] in first) for p in projects])
        + design.more([(f"All {len(build_cards.PROJECTS)} projects →", "/projects/"), ("GitHub as Suzume →", design.GITHUB_SUZUME),
                       ("GitHub as David →", design.GITHUB_DAVID)]), lensed=True)
    worlds = design.section("worlds", "Worlds",
        '<div class="wall">' + "".join(world_card(by_slug[s], True) for s in shown) + "".join(world_card(by_slug[s], False) for s in extra) + "</div>"
        + design.more([(f"See all {len(pieces)} pieces →", "/images.html")]),
        lensed=True, extra_head=f'<p class="lead">{WORLDS_INTRO}</p>')
    contact = ('<ul class="contact-list">' + "".join(f'<li><span class="contact-label">{label}</span><span>{links}</span></li>' for label, links in CONTACT) + "</ul>")

    body = f"""{design.header(home=True)}
<main id="main">
<section class="hero" id="top" data-room="{first_mood}"><div class="wrap hero-grid">
  <div class="hero-text">
    <h1>{H1}</h1>
    <p class="deck">{DECK}</p>
  </div>
  {show}
</div></section>

<div class="work" data-room="default" data-lens-room>
<div class="now-wrap"><div class="wrap"><div class="now-card">
  {nows()}
  {head_art()}
</div></div></div>

<section class="sec" id="research"><div class="wrap">
  <div class="sec-head"><h2>Research</h2></div>
  <p class="lead">{esc(build_topics.STATEMENT)}</p>
  <ul class="topics">{tiles}</ul>
</div></section>

<div class="lensed">
{design.lens_bar(TOPICS)}
{pubs}

{articles}

{projects_html}

{worlds}
</div>

<section class="sec contact" id="contact"><div class="wrap">
  <div class="sec-head"><h2>Contact</h2></div>
  <p class="lead">{CONTACT_LEDE}</p>
  {contact}
</div></section>
</div>
</main>
{design.footer(home=True)}
"""
    old = Path("index.html").read_text(encoding="utf-8")
    return design.listed(design.head(design.keep_meta(old), mood=first_mood) + body + design.END)

def build():
    Path("index.html").write_text(page(), encoding="utf-8")

if __name__ == "__main__":
    build()
    print("index.html rebuilt")
