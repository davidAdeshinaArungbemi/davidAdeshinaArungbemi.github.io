"""Builds the homepage's Articles and Projects cards from the lists below.

Run from the repo root:  python3 _tools/build_cards.py
Card images live in assets/cards/. The ones with no picture of their own are drawn by the
Processing sketch ~/Desktop/creative_coding/Covers. The script also reads the Medium feed
and names any article that isn't on the site yet.
"""
import html, re, urllib.request
from PIL import Image

FEED = "https://medium.com/feed/@suzume1"
MEDIUM = "https://suzume1.medium.com/"
FEATURED = MEDIUM + "dream-a-better-dream-6cff36484c35"      # shown above the cards, so not repeated

# (link, image, kind, title, line), newest first
ARTICLES = [
    ("https://doi.org/10.5281/zenodo.21294610", "assets/img/work-stories.jpg", "Preprint · 2026",
     "Narrative Transportation and Speciesism in Large Language Models",
     "After a story about an animal, language models expressed less prejudice toward it. The plain facts mostly didn't."),
    (MEDIUM + "you-are-what-you-prefer-2284ebdf1a00", "assets/img/work-preferences.jpg", "Essay & experiment · Sep 2026",
     "You Are What You Prefer",
     "Vanilla or caramel, as a fingerprint of a model's character — and an alarm for when it has quietly changed."),
    (MEDIUM + "in-brightest-day-in-blackest-night-no-evil-shall-escape-my-sight-47d54154abcb", "assets/cards/brightest-day.jpg", "Essay · Aug 2026",
     "In Brightest Day, In Blackest Night, No Evil Shall Escape My Sight.",
     "Why we tie evil to the dark, and where it hides when everything is lit: not in shadow, but in normality."),
    (MEDIUM + "who-deserves-moral-consideration-im-not-sure-anymore-ab2980ac549f", "assets/img/work-moral.jpg", "Essay · May 2026",
     "Who Deserves Moral Consideration? I’m Not Sure Anymore.",
     "If we can never see inside another mind, the question becomes what kind of people we want to be in our uncertainty."),
    (MEDIUM + "gestalt-the-whole-is-not-the-sum-of-its-parts-a4e5f1c61ef1", "assets/img/work-gestalt.jpg", "Experiment · Apr 2026",
     "Gestalt: The Whole is not the Sum of Its Parts",
     "Can different parts make the same whole? Very different starting images converge on almost the same picture."),
    (MEDIUM + "i-tried-to-build-an-aesthetic-model-of-the-human-brain-i-failed-heres-what-i-learned-13c75644258a", "assets/cards/aesthetic-model.jpg", "Experiment · Apr 2026",
     "I Tried to Build an Aesthetic Model of the Human Brain. I Failed. Here’s What I Learned.",
     "On neuroaesthetics, the BOLD5000 dataset, and what it means to optimise for beauty instead of truth."),
    (MEDIUM + "the-narrative-hypothesis-complexity-37bd4417575f", "assets/cards/complexity.jpg", "Essay · Apr 2026",
     "The Narrative Hypothesis: Complexity",
     "Every person carries a narrative. When narratives meet, new ones form: a family, a community, a nation."),
    (MEDIUM + "i-ran-the-experiment-here-is-what-i-found-d3052906ac86", "assets/cards/ran-the-experiment.png", "Experiment · Apr 2026",
     "I Ran the Experiment. Here Is What I Found.",
     "It didn't confirm the hypothesis. It showed what a real test would need to look like."),
    (MEDIUM + "the-narrative-hypothesis-f87be35619cf", "assets/cards/narrative-hypothesis.jpg", "Essay · Apr 2026",
     "The Narrative Hypothesis",
     "What if the universe is a story? Not as a metaphor, but as the way reality is still unfolding."),
    (MEDIUM + "i-gave-four-ai-agents-a-philosophy-and-put-them-under-pressure-8d6aa7f96dea", "assets/cards/four-agents.jpg", "Experiment · Mar 2026",
     "I Gave Four AI Agents a Philosophy and Put Them Under Pressure.",
     "Four agents, four philosophies, 640 turns of scarcity. Their words held; their choices loosened."),
    (MEDIUM + "inside-qwen-0-5b-a-behavioral-profile-across-32-dimensions-1ead43a6ea3c", "assets/cards/inside-qwen.jpg", "Experiment · Mar 2026",
     "Inside Qwen 0.5B: A Behavioral Profile Across 32 Dimensions",
     "Most evaluations measure what a model knows. This one asks how a small model behaves when you push it."),
]

# (link, image, kind, title, line, [(extra link text, url)])
SUZUME, DAVID = "https://github.com/suzume-hue/", "https://github.com/davidAdeshinaArungbemi/"
PROJECTS = [
    (SUZUME + "wen-s-mindscape", "assets/img/work-wen.jpg", "TypeScript · React · Three.js · 2026", "Wen's Mindscape",
     "An interactive portrait of a small language model: its behaviour across dozens of tests, given a face and a constellation you can explore.",
     [("Open the app", "https://wen-profile-dive.lovable.app/")]),
    (SUZUME + "llm-art-director", "assets/cards/llm-art-director.jpg", "Python · 2026", "LLM Art Director",
     "A language model that refines a photo by reasoning over aesthetic scorers, with a human-preference judge that can overrule the score.", []),
    (SUZUME + "DiverseIntelligence", "assets/cards/diverse-intelligence.jpg", "Python · in progress", "DiverseIntelligence",
     "A multi-agent engine where minds that think differently must pass through a translation layer before they can answer each other.", []),
    (SUZUME + "Gestalt", "assets/cards/gestalt-project.jpg", "Python · 2026", "Gestalt",
     "Whether different images can add up to the same whole, by optimising for structure, meaning and beauty at once.",
     [("Write-up", MEDIUM + "gestalt-the-whole-is-not-the-sum-of-its-parts-a4e5f1c61ef1")]),
    (SUZUME + "AestheticsOptimizer", "assets/cards/aesthetics-optimizer.jpg", "Python · 2026", "Aesthetics Optimizer",
     "A personalised model of how one person's brain responds to images, from fMRI data, with a desktop app that grows generative art toward it.",
     [("Write-up", MEDIUM + "i-tried-to-build-an-aesthetic-model-of-the-human-brain-i-failed-heres-what-i-learned-13c75644258a")]),
    (DAVID + "BitRNN", "assets/cards/bitrnn.png", "C++ · 2025", "BitRNN",
     "A recurrent network whose weights are single bits, trained by evolution instead of gradients.", []),
    (DAVID + "Story-GRU-LM-and-Interpretability", "assets/cards/story-gru.jpg", "Python · 2025", "Story GRU language model",
     "A small story-writing model, and what its hidden states reveal as meaning forms.",
     [("Notebook (PDF)", "Notebooks/story-gru-lm.pdf")]),
    (DAVID + "Narrative-Technical-Embedding-Space", "assets/cards/narrative-technical.jpg", "Python · 2025", "Narrative–Technical Embedding Space",
     "Teaching a model to tell stories apart from technical writing, as a first step toward translating between them.", []),
    (DAVID + "Tarot-VAE", "assets/cards/tarot-vae.jpg", "Python · 2025", "Tarot-VAE",
     "A patch-based VAE that learns to rebuild and invent tarot-style cards.", []),
    (DAVID + "SceneGraph", "assets/cards/scenegraph.jpg", "Python · 2025", "SceneGraph",
     "A live graph of the people and objects in a video stream.", []),
    (DAVID + "SMLF-Library", "assets/cards/smlf.jpg", "C++ · 2023", "SMLF",
     "A machine-learning library and a dataframe, written from scratch in C++ to see what's underneath.",
     [("OurDataframe", DAVID + "OurDataframe")]),
]

esc = lambda s: html.escape(s, quote=False)

def card(link, img, kind, title, line, extras=()):
    w, h = Image.open(img).size
    out = ['    <article class="pin card">',
           f'      <a class="card-link" href="{link}">',
           f'        <div class="pin-media"><img src="{img}" alt="" width="{w}" height="{h}" loading="lazy"></div>',
           f'        <p class="card-kind">{esc(kind)}</p>',
           f'        <h3 class="card-title">{esc(title)}</h3>',
           f'        <p class="card-line">{esc(line)}</p>',
           '      </a>']
    if extras:
        out.append('      <p class="card-extra">' + "".join(f'<a href="{u}">{esc(t)}</a>' for t, u in extras) + '</p>')
    out.append('    </article>')
    return "\n".join(out)

def fill(page, name, cards):
    pattern = re.compile(rf"(<!-- cards:{name} -->).*?([ \t]*<!-- /cards:{name} -->)", re.S)
    assert pattern.search(page), f"no <!-- cards:{name} --> markers in index.html"
    return pattern.sub(lambda m: m.group(1) + "\n" + "\n".join(cards) + "\n" + m.group(2), page)

def check_medium():
    try:
        req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (Macintosh)"})
        xml = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    except Exception as e:
        print("Couldn't read the Medium feed:", e)
        return
    on_site = {a[0] for a in ARTICLES} | {FEATURED}
    for it in re.findall(r"<item>(.*?)</item>", xml, re.S):
        link = re.search(r"<link>(.*?)</link>", it).group(1).split("?")[0]
        if link not in on_site:
            title = html.unescape(re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", it, re.S).group(1)).strip()
            print(f"Not on the site yet: {title}\n  {link}")

def build():
    page = open("index.html", encoding="utf-8").read()
    page = fill(page, "articles", [card(*a) for a in ARTICLES])
    page = fill(page, "projects", [card(*p) for p in PROJECTS])
    open("index.html", "w", encoding="utf-8").write(page)
    print(f"index.html: {len(ARTICLES)} article cards · {len(PROJECTS)} project cards")
    check_medium()

if __name__ == "__main__":
    build()
