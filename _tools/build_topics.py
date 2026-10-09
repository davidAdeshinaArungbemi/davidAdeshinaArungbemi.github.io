"""The four topic pages (/stories-and-ai/, /aesthetics/, /visualisation/, /minds/), the projects page
(/projects/) and the homepage's Research section, built from the same projects, articles, publications
and images the other scripts use. Each topic page is something a professor can be sent straight to.

Run from the repo root, after build_cards.py, build_blog.py and build_gallery.py (needs bs4, like build_blog.py):
  python3 _tools/build_topics.py
"""
import re
from pathlib import Path
from build_cards import PROJECTS, TAGS, SUZUME, DAVID
from build_blog import load_all, head, topbar, FOOT, month, smaller, SITE
from build_gallery import GROUPS, VIDEOS
from rows import row, esc, attr

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

def item_row(kind, key):
    if kind == "pub":
        link, img, label, title, line, tags, extras = PUBS[key]
        return row(link, img, label, title, line, tags, extras)
    if kind == "article":
        p = POSTS[key]
        return row(f"/articles/{key}/", smaller(p["cover"]), f"{p['kind']} · {month(p['date'])}", p["title"], p["line"], p.get("tags", ()))
    if kind == "project":
        link, img, label, title, line, extras = PROJ[key]
        return row(link, img, label, title, line, TAGS[title], extras)
    slug, title, meta, caption, _ = IMAGES[key]
    img = VIDEOS[slug][1] if slug in VIDEOS else f"assets/gallery/{slug}-800.jpg"
    return row(f"/images.html#{slug}", img, meta, title, caption)

def image_tile(key):
    slug, title, meta, caption, alt = IMAGES[key]
    img = VIDEOS[slug][1] if slug in VIDEOS else f"assets/gallery/{slug}-800.jpg"
    return (f'    <li><a href="/images.html#{slug}"><img src="/{img}" alt="{attr(alt or title)}" loading="lazy">'
            f'<span>{esc(title)}</span></a></li>')

def section(title, rows):
    return f'<section>\n  <h2 class="eyebrow">{title}</h2>\n  <ol class="rows">\n' + "\n".join(rows) + "\n  </ol>\n</section>\n" if rows else ""

def topic_page(t):
    started = set(t["start"])
    rest = [i for i in t["items"] if i not in started]
    pubs = [item_row(*i) for i in rest if i[0] == "pub"]
    exps = [item_row(*i) for i in rest if i[0] == "article" and is_experiment(POSTS[i[1]])]
    projs = [item_row(*i) for i in rest if i[0] == "project"]
    essays = [item_row(*i) for i in rest if i[0] == "article" and not is_experiment(POSTS[i[1]])]
    imgs = [image_tile(i[1]) for i in rest if i[0] == "image"]
    others = " · ".join(f'<a href="/{o["slug"]}/">{esc(o["title"])}</a>' for o in TOPICS if o is not t)
    images = (f'<section>\n  <h2 class="eyebrow">Images</h2>\n  <ul class="topic-images">\n' + "\n".join(imgs)
              + '\n  </ul>\n  <p class="see-all"><a href="/images.html">All of Worlds →</a></p>\n</section>\n') if imgs else ""
    cover = next((smaller(POSTS[k]["cover"]) if kind == "article" else "/" + (PUBS[k][1] if kind == "pub" else PROJ[k][1]))
                 for kind, k in t["start"] if kind != "image")
    return (head(f"{t['title']} · David Adeshina Arungbemi", f"{t['title']}: {t['line']} Work by David Adeshina Arungbemi.",
                 f"{SITE}/{t['slug']}/", cover) + topbar() + f"""
<main id="main">
<section class="page-head topic-head">
  <p class="topic-kicker">Research topic</p>
  <h1>{esc(t['title'])}</h1>
  <p class="topic-statement">{esc(t['statement'])}</p>
  <p class="topic-others">Other topics: {others}</p>
</section>
<section>
  <h2 class="eyebrow">Start with</h2>
  <ol class="rows rows-start">
{chr(10).join(item_row(*i) for i in t['start'])}
  </ol>
</section>
""" + section("Publications", pubs) + section("Experiments", exps) + section("Projects", projs) + section("Essays", essays)
            + images + "</main>\n\n" + FOOT)

def projects_page():
    rows = "\n".join(row(l, i, k, t, ln, TAGS[t], ex) for l, i, k, t, ln, ex in PROJECTS)
    return (head("Projects · David Adeshina Arungbemi", "Code projects by David Adeshina Arungbemi, who also writes as Suzume.",
                 f"{SITE}/projects/", "/assets/cards/llm-art-director.jpg") + topbar("Projects") + f"""
<main id="main">
<section class="page-head">
  <h1>Projects</h1>
  <p>Code, from my own GitHub (David) and my pen name's (Suzume). For the ideas behind them, start from a <a href="/#research">research topic</a>.</p>
</section>
<section>
  <ol class="rows">
{rows}
  </ol>
  <p class="see-all"><a href="{SUZUME}">GitHub as Suzume →</a><a href="{DAVID}">GitHub as David →</a></p>
</section>
</main>

""" + FOOT)

def research_block():
    tiles = "\n".join(
        f'    <li><a href="/{t["slug"]}/"><span class="topic-title">{esc(t["title"])}</span>'
        f'<span class="topic-line">{esc(t["line"])}</span>'
        f'<span class="topic-count">{len(set(t["start"]) | set(t["items"]))} pieces →</span></a></li>' for t in TOPICS)
    return f'  <p class="research-statement">{esc(STATEMENT)}</p>\n  <ul class="topics">\n{tiles}\n  </ul>'

def build():
    for t in TOPICS:
        out = Path(t["slug"]); out.mkdir(exist_ok=True)
        (out / "index.html").write_text(topic_page(t), encoding="utf-8")
    Path("projects").mkdir(exist_ok=True)
    Path("projects/index.html").write_text(projects_page(), encoding="utf-8")
    page = Path("index.html").read_text(encoding="utf-8")
    pattern = re.compile(r"(<!-- research -->).*?([ \t]*<!-- /research -->)", re.S)
    assert pattern.search(page), "no <!-- research --> markers in index.html"
    page = pattern.sub(lambda m: m.group(1) + "\n" + research_block() + "\n" + m.group(2), page)
    Path("index.html").write_text(page, encoding="utf-8")
    print(f"{len(TOPICS)} topic pages, projects/ ({len(PROJECTS)}), homepage research section")

if __name__ == "__main__":
    build()
