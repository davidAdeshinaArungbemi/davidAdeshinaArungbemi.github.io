"""The projects. The homepage lists a few of them (HOME below) as plain rows; build_topics.py builds
the projects page (/projects/) with all of them. (Articles come from _tools/build_blog.py.)

Run from the repo root:  python3 _tools/build_cards.py
Card images live in assets/cards/. The ones with no picture of their own are drawn by the
Processing sketch ~/Desktop/creative_coding/Covers.
"""
import re
from rows import row

# (link, image, kind, title, line, [(extra link text, url)])
SUZUME, DAVID = "https://github.com/suzume-hue/", "https://github.com/davidAdeshinaArungbemi/"
PROJECTS = [
    (SUZUME + "wen-s-mindscape", "assets/img/work-wen.jpg", "TypeScript · React · 2026", "Wen's Mindscape",
     "An interactive profile of a small language model, Qwen 2.5 0.5B, drawn as a spirit called Wen: its real answers across 32 kinds of behaviour, as charts and a constellation you can explore.",
     [("Open the app", "https://wen-profile-dive.lovable.app/")]),
    (SUZUME + "llm-art-director", "assets/cards/llm-art-director.jpg", "Python · 2026", "LLM Art Director",
     "A language model that art-directs an image, ordering edits round by round from aesthetic scores. A model of human preference undoes any edit that raises the scores but that a person would probably like less.", []),
    (SUZUME + "DiverseIntelligence", "assets/cards/diverse-intelligence.jpg", "Python · in progress", "DiverseIntelligence",
     "A multi-agent engine where minds that think differently must pass through a translation layer before they can answer each other.", []),
    (SUZUME + "Gestalt", "assets/cards/gestalt-project.jpg", "Python · 2026", "Gestalt",
     "Asks whether different images can add up to the same whole, by optimising them for structure, meaning and beauty at once.",
     [("Write-up", "articles/gestalt/")]),
    (SUZUME + "AestheticsOptimizer", "assets/cards/aesthetics-optimizer.jpg", "Python · 2026", "Aesthetics Optimizer",
     "An attempt to predict the brain's fMRI response to a new image, personalised from a person's ranked image history, and a desktop app that tunes generative art to raise the prediction. The predictions were weak (mean r about 0.08), and the write-up covers why.",
     [("Write-up", "articles/aesthetic-model/")]),
    (DAVID + "BitRNN", "assets/cards/bitrnn.png", "C++ · 2025", "BitRNN",
     "A recurrent network whose weights are single bits, trained by evolution instead of gradients.", []),
    (DAVID + "Story-GRU-LM-and-Interpretability", "assets/cards/story-gru.jpg", "Python · 2025", "Story GRU language model",
     "A small model that writes stories, and a look inside it at how meaning builds up, word by word.",
     [("Notebook (PDF)", "Notebooks/story-gru-lm.pdf")]),
    ("Notebooks/vq-vae-codeword-visualisation-and-sequencing.pdf", "assets/cards/codebook-genome.jpg", "Python · notebook · 2025", "Codebook Genome",
     "A VQ-VAE turns each small image into a sequence of 64 codes, and the notebook reads them like DNA: as a strand, a grid and a ring, so every image has its own genome.", []),
    ("Notebooks/deterministic-inpainting.pdf", "assets/cards/inpainting.jpg", "Python · notebook · 2025", "Deterministic Inpainting",
     "Restoring Symbolist paintings from WikiArt with 30% of their pixels knocked out. The model works patch by patch and also predicts which pixels were missing. The results keep the colour and layout but stay blurry.", []),
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

# Topic tags shown under each card, by title
TAGS = {
    "Wen's Mindscape": ["Model evaluation", "Language models", "Data visualisation"],
    "LLM Art Director": ["Language models", "Image editing", "Computational aesthetics"],
    "DiverseIntelligence": ["Multi-agent", "Language models"],
    "Gestalt": ["Neuroaesthetics", "Image generation", "Perception"],
    "Aesthetics Optimizer": ["Neuroaesthetics", "fMRI", "Generative art"],
    "BitRNN": ["Evolutionary training", "Binary networks", "From scratch"],
    "Story GRU language model": ["Language models", "Interpretability", "Stories"],
    "Codebook Genome": ["VQ-VAE", "Representation learning", "Visualisation"],
    "Deterministic Inpainting": ["Computer vision", "Image restoration", "Art"],
    "Narrative–Technical Embedding Space": ["Embeddings", "Narrative", "Contrastive learning"],
    "Tarot-VAE": ["Generative models", "VAE", "Art"],
    "SceneGraph": ["Computer vision", "Scene graphs", "Video"],
    "SMLF": ["From scratch", "C++", "ML library"],
}
missing = [p[3] for p in PROJECTS if p[3] not in TAGS]
assert not missing, f"no tags for {missing}"

# The homepage lists these; the projects page (/projects/, built by build_topics.py) lists them all
HOME = ["Wen's Mindscape", "LLM Art Director", "Gestalt", "Aesthetics Optimizer", "Story GRU language model", "Codebook Genome"]
assert all(t in [p[3] for p in PROJECTS] for t in HOME)

def project_row(p):
    link, img, kind, title, line, extras = p
    return row(link, img, kind, title, line, TAGS[title], extras)

def fill(page, name, items):
    pattern = re.compile(rf"(<!-- cards:{name} -->).*?([ \t]*<!-- /cards:{name} -->)", re.S)
    assert pattern.search(page), f"no <!-- cards:{name} --> markers in index.html"
    return pattern.sub(lambda m: m.group(1) + "\n" + "\n".join(items) + "\n" + m.group(2), page)

def build():
    page = open("index.html", encoding="utf-8").read()
    by = {p[3]: p for p in PROJECTS}
    page = fill(page, "projects", [project_row(by[t]) for t in HOME])
    page = re.sub(r"All \d+ projects", f"All {len(PROJECTS)} projects", page)
    open("index.html", "w", encoding="utf-8").write(page)
    print(f"index.html: {len(HOME)} of {len(PROJECTS)} projects")

if __name__ == "__main__":
    build()
