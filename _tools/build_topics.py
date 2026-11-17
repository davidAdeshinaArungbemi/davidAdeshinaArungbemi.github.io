"""The four topic pages (/stories-and-ai/, /aesthetics/, /visualisation/, /minds/) and the projects page
(/projects/), built from the same projects, articles, publications and images the other scripts use. Each topic
page is something a professor can be sent straight to. The homepage's Research section uses TOPICS and STATEMENT
too (build_home.py, which this script runs at the end).

Run from the repo root, after build_cards.py, build_gallery.py and build_blog.py:
  python3 _tools/build_topics.py
"""
from pathlib import Path
import design
from design import esc, attr
from build_cards import PROJECTS, TAGS, SUZUME, DAVID
from build_blog import load_all, month, smaller, SITE
from build_gallery import GROUPS, VIDEOS

STATEMENT = ("I'm interested in how stories and images shape minds, human and artificial. Most of my work takes a "
             "humanistic question, such as what a story teaches, what makes an image beautiful, or who deserves moral "
             "consideration, turns it into a small experiment on an AI model, and reports honestly whether the idea held.")

PUBS = {
    "preprint": ("https://doi.org/10.5281/zenodo.21294610", "assets/img/work-stories.jpg", "Preprint · not peer-reviewed · 2026",
                 "Narrative Transportation and Speciesism in Large Language Models",
                 "Five models read a story about an animal, the same facts written plainly, or nothing, then answered a speciesism "
                 "questionnaire. On the questions about that animal, their speciesism, already modest, fell to nearly zero after "
                 "the story; the plain facts generally did not change it. The effects were small in absolute terms.",
                 ["Narrative", "Language models", "Animal welfare"],
                 [("PDF", "https://zenodo.org/records/21294610/files/arungbemi-2026-narrative-transportation-speciesism-llms.pdf")]),
    "gestures": ("https://doi.org/10.1109/ACCESS.2025.3602871", "assets/cards/gestures.jpg", "Journal article · peer-reviewed · 2025",
                 "An End to End Wearable Device and System for Indefinite, Continuous, Real Time Gesture Recognition of Directional and Shape-Based Arm Gestures",
                 "Co-author, IEEE Access. A wearable that recognises arm gestures continuously and in real time; I designed its AI, "
                 "from the raw motion data to the model that names each gesture, and the interface of the live app.",
                 ["Gesture recognition", "Interaction"], []),
}

# Items are (kind, key): ("pub", key in PUBS), ("article", slug), ("project", title), ("image", Worlds slug)
TOPICS = [
    dict(slug="stories-and-ai", title="Stories and AI", line="How stories change what language models say and do.",
         statement=("Can a story change the positions a language model expresses, the way a story can change a person's? In my "
                    "preprint, stories about an animal reduced speciesism in five models' answers about that animal, while the same "
                    "facts written plainly generally did not. The effects were small in absolute terms, the questionnaire was my own "
                    "rather than a validated scale, and the stories were drafted with a language model, so it is a first result, not a "
                    "settled one. At MARS I'm now testing whether fine-tuning on stories can carry a story's "
                    "lesson into a model's weights, so the model acts on it without the story in front of it. Related experiments "
                    "profile how a small model behaves when pushed, test whether stated values hold under pressure, and ask "
                    "whether small preferences can show when a model has changed."),
         start=[("pub", "preprint"), ("article", "inside-qwen")],
         items=[("article", "you-are-what-you-prefer"), ("article", "four-agents"), ("article", "i-ran-the-experiment"),
                ("project", "Wen's Mindscape"), ("project", "DiverseIntelligence"), ("project", "Narrative–Technical Embedding Space"),
                ("project", "Story GRU language model"), ("article", "the-narrative-hypothesis"),
                ("article", "narrative-hypothesis-complexity"), ("article", "who-deserves-moral-consideration"),
                ("image", "value-chords"), ("image", "prefer-cover")]),
    dict(slug="aesthetics", title="Aesthetics and perception", line="What images do to minds, and what models make of beauty.",
         statement=("What happens when we look at an image and find it beautiful, and can a model learn any of it? I tried to "
                    "predict brain responses to images from fMRI data; it largely failed, and the write-up says why. I tested "
                    "whether very different starting images can be pushed toward the same target, as judged by image models (not yet "
                    "by people), and built a system in "
                    "which a language model edits an image guided by aesthetic scores, with a model of human preference to catch "
                    "edits that only game the scores. I haven't yet run studies with people; that is the step these questions need "
                    "next. I also draw, paint and make generative art, and that practice is where most of these questions start."),
         start=[("article", "gestalt"), ("article", "aesthetic-model")],
         items=[("project", "Aesthetics Optimizer"), ("project", "Gestalt"), ("project", "LLM Art Director"),
                ("project", "Codebook Genome"), ("project", "Deterministic Inpainting"), ("project", "Tarot-VAE"),
                ("article", "dream-a-better-dream"), ("article", "the-question-was-mine"), ("article", "the-mind-and-its-power"),
                ("image", "pencil-studies-2022"), ("image", "face-shaded-2022"), ("image", "caustic-bloom"), ("image", "water-town"),
                ("image", "night-walk"), ("image", "skull-2021"), ("image", "art-of-intelligence"), ("image", "calligraphy")]),
    dict(slug="visualisation", title="Visualisation and interaction",
         line="Making model behaviour and complex ideas visible, and letting people shape them.",
         statement=("Much of what models do is hard to see, so I build ways to look at it: an app for exploring a small model's "
                    "behaviour across 32 dimensions, generative pieces that show a value system from different sides, and pictures "
                    "of how an image model encodes what it sees. Before that I worked on interaction directly: I designed the AI "
                    "of a wearable that recognises arm gestures continuously and in real time. None of the visual tools here has been "
                    "tested with users yet."),
         start=[("project", "Wen's Mindscape"), ("image", "value-tomography")],
         items=[("pub", "gestures"), ("article", "inside-qwen"), ("project", "Codebook Genome"), ("project", "LLM Art Director"),
                ("project", "SceneGraph"), ("article", "sculpting-latent-space"), ("article", "dream-a-better-dream"),
                ("image", "value-chords"), ("image", "art-of-intelligence"), ("image", "poster-variations"),
                ("image", "ripples-crab"), ("image", "gyronics-axol")]),
    dict(slug="minds", title="Minds and meaning", line="How meaning forms, in people and in models.",
         statement=("The questions underneath the rest: how sound turns into meaning, whether a system could reason in steps we "
                    "can read, why we tie evil to the dark, and who counts as a mind at all. Most of this is essays. The "
                    "experimental side is small: a story-writing model whose inner workings I probed to watch meaning build up, "
                    "word by word."),
         start=[("article", "sound-and-meaning"), ("article", "who-deserves-moral-consideration")],
         items=[("project", "Story GRU language model"), ("article", "self-reasoning-system"), ("article", "interpretability-trap"),
                ("article", "in-brightest-day"), ("article", "the-narrative-hypothesis"), ("article", "narrative-hypothesis-complexity")]),
]

POSTS = {p["slug"]: p for p in load_all()}
PROJ = {p[3]: p for p in PROJECTS}
IMAGES = {it[0]: it for _, _, _, items in GROUPS for it in items}

def is_experiment(p): return "experiment" in p["kind"].lower()

def picture(slug):
    return "/" + VIDEOS[slug][1] if slug in VIDEOS else f"/assets/gallery/{slug}-800.jpg"

def item_card(kind, key, level=3):
    """Any piece as a card."""
    if kind == "pub":
        link, img, label, title, line, tags, extras = PUBS[key]
        return design.card(link, img, label, title, line, tags, extras, level=level)
    if kind == "article":
        p = POSTS[key]
        return design.card(f"/articles/{key}/", smaller(p["cover"]), f"{p['kind']} · {month(p['date'])}", p["title"], p["line"],
                           p.get("tags", ()), level=level)
    if kind == "project":
        link, img, label, title, line, extras = PROJ[key]
        return design.card(link, img, label, title, line, TAGS[title], extras, level=level)
    slug, title, meta, caption, _ = IMAGES[key]
    return design.card(f"/images.html#{slug}", picture(slug), meta, title, caption, level=level)

def image_card(key):
    slug, title, meta, caption, alt = IMAGES[key]
    return design.world(slug, title, meta, caption, alt or VIDEOS[slug][4], poster=picture(slug) if slug in VIDEOS else None)

def topic_page(t):
    started = set(t["start"])
    rest = [i for i in t["items"] if i not in started]
    def part(title, items, cls=""):
        return design.section(None, title, design.cards([item_card(*i) for i in items], cls)) if items else ""
    pubs = [i for i in rest if i[0] == "pub"]
    exps = [i for i in rest if i[0] == "article" and is_experiment(POSTS[i[1]])]
    projs = [i for i in rest if i[0] == "project"]
    essays = [i for i in rest if i[0] == "article" and not is_experiment(POSTS[i[1]])]
    imgs = [i[1] for i in rest if i[0] == "image"]
    images = (design.section(None, "Images", '<div class="wall">' + "".join(image_card(k) for k in imgs) + "</div>"
                             + design.more([("All of Worlds →", "/images.html")]))) if imgs else ""
    tabs = "".join(f'<a class="tab" href="/{o["slug"]}/" data-mood="topic-{o["slug"]}">{esc(o["title"])}</a>' for o in TOPICS if o is not t)
    cover = next((smaller(POSTS[k]["cover"]) if kind == "article" else "/" + (PUBS[k][1] if kind == "pub" else PROJ[k][1]))
                 for kind, k in t["start"] if kind != "image")
    meta = design.meta(f"{t['title']} · David Adeshina Arungbemi", f"{t['title']}: {t['line']} Work by David Adeshina Arungbemi.",
                       f"{SITE}/{t['slug']}/", cover)
    return design.listed(design.head(meta, mood=f"topic-{t['slug']}", rss=True) + design.header(current="Research") + f"""
<main id="main">
<section class="band-wrap"><div class="wrap"><div class="band">
  <p class="kicker">Research topic</p>
  <h1>{esc(t['title'])}</h1>
  <p class="statement">{esc(t['statement'])}</p>
  <nav class="tabs" aria-label="Other topics"><span class="tabs-label" aria-hidden="true">Other topics</span>{tabs}</nav>
</div></div></section>
""" + part("Start with", t["start"], " is-start") + part("Publications", pubs) + part("Experiments", exps) + part("Projects", projs)
        + part("Essays", essays) + images + "</main>\n" + design.footer() + "\n" + design.END)

def projects_page():
    cards = design.cards([design.card(l, i, k, t, ln, TAGS[t], ex, level=2) for l, i, k, t, ln, ex in PROJECTS])
    meta = design.meta("Projects · David Adeshina Arungbemi", "Code projects by David Adeshina Arungbemi, who also writes as Suzume.",
                       f"{SITE}/projects/", "/assets/cards/llm-art-director.jpg")
    return design.listed(design.head(meta, rss=True) + design.header(current="Projects") + f"""
<main id="main">
<section class="page-head"><div class="wrap">
  <h1>Projects</h1>
  <p>Code, from my own GitHub (David) and my pen name's (Suzume). For the ideas behind them, start from a <a href="/#research">research topic</a>.</p>
</div></section>
<section class="sec"><div class="wrap">
  {cards}
  <p class="more"><a href="{SUZUME}">GitHub as Suzume →</a><a href="{DAVID}">GitHub as David →</a></p>
</div></section>
</main>
""" + design.footer() + "\n" + design.END)

def check_topics():
    """Stop with a plain message if a topic names a piece that doesn't exist, or has no colour."""
    known = {"pub": PUBS, "article": POSTS, "project": PROJ, "image": IMAGES}
    for t in TOPICS:
        if t["slug"] not in design.TOPIC_HUES:
            raise SystemExit(f"topic {t['slug']}: add its hue to design.TOPIC_HUES")
        for kind, key in list(t["start"]) + list(t["items"]):
            if kind not in known:
                raise SystemExit(f"topic {t['slug']}: unknown kind '{kind}' (use pub, article, project or image)")
            if key not in known[kind]:
                raise SystemExit(f"topic {t['slug']}: no {kind} called '{key}'")

def build():
    check_topics()
    design.write_moods()                                    # first, so every page names the current palettes file
    for t in TOPICS:
        out = Path(t["slug"]); out.mkdir(exist_ok=True)
        (out / "index.html").write_text(topic_page(t), encoding="utf-8")
    Path("projects").mkdir(exist_ok=True)
    Path("projects/index.html").write_text(projects_page(), encoding="utf-8")
    print(f"{len(TOPICS)} topic pages, projects/ ({len(PROJECTS)})")
    design.finish()

if __name__ == "__main__":
    build()
