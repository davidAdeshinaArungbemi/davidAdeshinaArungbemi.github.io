"""Builds the homepage's Projects cards from the list below. (The Articles cards come from
_tools/build_blog.py, which also builds the article pages.)

Run from the repo root:  python3 _tools/build_cards.py
Card images live in assets/cards/. The ones with no picture of their own are drawn by the
Processing sketch ~/Desktop/creative_coding/Covers.
"""
import html, re
from PIL import Image

# (link, image, kind, title, line, [(extra link text, url)])
SUZUME, DAVID = "https://github.com/suzume-hue/", "https://github.com/davidAdeshinaArungbemi/"
PROJECTS = [
    (SUZUME + "wen-s-mindscape", "assets/img/work-wen.jpg", "TypeScript · React · Three.js · 2026", "Wen's Mindscape",
     "An interactive portrait of a small language model: its behaviour across dozens of tests, given a face and a constellation you can explore.",
     [("Open the app", "https://wen-profile-dive.lovable.app/")]),
    (SUZUME + "llm-art-director", "assets/cards/llm-art-director.jpg", "Python · 2026", "LLM Art Director",
     "A language model that refines a photo by reasoning over aesthetic scorers, with a pretrained human-preference model (PickScore) that can overrule the score.", []),
    (SUZUME + "DiverseIntelligence", "assets/cards/diverse-intelligence.jpg", "Python · in progress", "DiverseIntelligence",
     "A multi-agent engine where minds that think differently must pass through a translation layer before they can answer each other.", []),
    (SUZUME + "Gestalt", "assets/cards/gestalt-project.jpg", "Python · 2026", "Gestalt",
     "Whether different images can add up to the same whole, by optimising for structure, meaning and beauty at once.",
     [("Write-up", "articles/gestalt/")]),
    (SUZUME + "AestheticsOptimizer", "assets/cards/aesthetics-optimizer.jpg", "Python · 2026", "Aesthetics Optimizer",
     "A personalised model of how one person's brain responds to images, from fMRI data, with a desktop app that grows generative art toward it.",
     [("Write-up", "articles/aesthetic-model/")]),
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

def build():
    page = open("index.html", encoding="utf-8").read()
    page = fill(page, "projects", [card(*p) for p in PROJECTS])
    open("index.html", "w", encoding="utf-8").write(page)
    print(f"index.html: {len(PROJECTS)} project cards")

if __name__ == "__main__":
    build()
