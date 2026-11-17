"""The page David opens first: the three directions side by side, what I need from him, and the audit.

Built by build.py into _directions/index.html. Plain words, short, and big enough to read easily.
"""
import re
from html import unescape as html_unescape
from pathlib import Path

import kit
import content as c
import check

OUT = kit.OUT
esc, attr = kit.esc, kit.attr

DIRS = [
    ("d", "A and B mixed", "B's way through your work, inside A's room.", [
        ("Colour", "At the top, the clip that is playing lights the room, as in A. Below it, the topic you choose lights it and brings that topic's work forward, as in B. A card you point at takes its own picture's colours."),
        ("Moving around", "Plain links at the top (one row you can swipe on a phone), and a topic bar that stays in view as you scroll."),
    ]),
    ("a", "The screen", "A dark room lit by whatever is showing.", [
        ("Colour", "The room takes its light from the clip that is playing, and from any piece you point at or tab to. In an article it changes with each picture you pass."),
        ("Moving around", "A bar at the bottom of the screen. On a phone it keeps Research, Publications and CV, and the rest goes under Menu."),
    ]),
    ("b", "Four lenses", "Your four research topics are the way in.", [
        ("Colour", "Choose a topic and the whole page takes its colour, while that topic's work comes forward in every section. The showcase frame takes the colour of the clip that is playing, and a card you point at takes its own picture's colours."),
        ("Moving around", "Plain links at the top, and a topic bar that stays in view as you scroll."),
    ]),
    ("c", "Rooms", "Each part of the homepage is a room of its own.", [
        ("Colour", "As you walk from room to room the page changes colour, and between light and dark, following each room's picture. In an article every picture changes the scene. This one follows what you wrote about March Comes in Like a Lion: the world and the feelings moving together. If your device is set to dark, every room stays dark."),
        ("Moving around", "A small map of the rooms at the side of a wide screen, with CV in it. On smaller screens it is a Menu button."),
    ]),
]

PAGES = [("index.html", "Homepage"), (f"{kit.TOPIC}.html", "Topic page"), (f"{kit.ARTICLE}.html", "Article")]

CLIP_IDEAS = [
    ("Colour Bird", "it sways and blinks"),
    ("Value Tomography", "it turns"),
    ("Value Chords", "a click lights up one path"),
    ("Ripples and Caustic Bloom", "both run frame by frame, so they may give a clip"),
    ("The robot arms drawing", "the 11 second clip already on some of your tailored pages"),
    ("Matsumoto", "later, once that piece is done"),
]

JS_STRINGS = {   # strings the scripts write at run time (check.py only sees the HTML)
    "A B C": ["Pause the showcase", "Play the showcase", "Pause", "Play", "Clip 2 of 3: Animation exercise (said when you pick a clip)",
              "carousel (what a screen reader calls the showcase)", "slide", "1 of 3 (each clip's place)"],
    "A B": ["Switch to light", "Switch to dark"],
    "B": ["Showing Stories and AI (said when you choose a topic)", "11 of 18 (each section's count)", "Stories and AI page → (the chosen topic's name)"],
}

def tokens(d, mood):
    """(ground, ink) of a mood as that direction's moods.css first defines it (its default scheme)."""
    css = (OUT / d / "moods.css").read_text(encoding="utf-8")
    m = re.search(r'\[data-mood="' + re.escape(mood) + r'"\]\{([^}]*)\}', css)
    if not m:
        return None
    g = re.search(r"--ground:(#[0-9A-Fa-f]{6})", m.group(1))
    k = re.search(r"--ink:(#[0-9A-Fa-f]{6})", m.group(1))
    return (g.group(1), k.group(1)) if g and k else None

def journey(d):
    """The colours a direction moves through, with what brings each one, in page order."""
    page = (OUT / d / "index.html").read_text(encoding="utf-8")
    steps = []
    if d in ("a", "d"):
        for mood, title in re.findall(r'data-slide data-src="[^"]*" data-mood="([^"]+)"[^>]*data-title="([^"]+)"', page):
            steps.append((html_unescape(title), mood))
    if d == "d":
        steps += [(t["title"], "topic-" + t["slug"]) for t in c.TOPICS]
    elif d == "b":
        steps.append(("All", "default"))
        steps += [(t["title"], "topic-" + t["slug"]) for t in c.TOPICS]
    else:
        part = page.split('class="c-map"', 1)[1].split("</nav>", 1)[0] if 'class="c-map"' in page else ""
        labels = {k: re.sub(r"<[^>]+>", "", v).strip() for k, v in re.findall(r'<a href="#([a-z-]+)"[^>]*>(.*?)</a>', part)}
        for tag in re.findall(r"<section\b[^>]*>", page):
            room = re.search(r'data-room="([^"]+)"', tag)
            rid = re.search(r'\bid="([^"]+)"', tag)
            if room and rid:
                steps.append((labels.get(rid.group(1), rid.group(1).title()), room.group(1)))
    chips = []
    for label, mood in steps:
        t = tokens(d, mood)
        if t:
            chips.append(f'<li style="background:{t[0]};color:{t[1]}">{esc(label)}</li>')
    return '<ul class="journey" aria-label="Colours it moves through">' + "".join(chips) + "</ul>" if chips else ""

def public_pages():
    rows = [("/", "Homepage"), ("/cv.html", "CV"), ("/images.html", "Worlds (106 pieces)"), ("/articles/", "Articles")]
    rows += [(f"/articles/{p['slug']}/", p["title"]) for p in c.POSTS]
    rows += [("/projects/", "Projects (13)")] + [(f"/{t['slug']}/", t["title"]) for t in c.TOPICS]
    rows += [("/404.html", "Page not found (not in the sitemap)")]
    return rows

def unlisted():
    root = Path("for")
    pages = sorted(p.parent.relative_to(".").as_posix() for p in root.glob("*/index.html"))
    cvs = sorted(p.parent.relative_to(".").as_posix() for p in root.glob("*/cv/index.html"))
    return pages, cvs

def shot(d):
    p = OUT / "shared" / "shots" / f"{d}.jpg"
    if not p.exists():
        return ""
    from PIL import Image
    w, h = Image.open(p).size
    return f'<img class="shot" src="shared/shots/{d}.jpg" alt="" width="{w}" height="{h}" loading="lazy">'

def strings_html():
    found = check.new_strings(["a", "b", "c"])
    # his own labels and tags (from _writing headers and build_cards.TAGS) aren't interface words
    his = {t for p in c.POSTS for t in p.get("tags", ())} | {t for ts in c.build_cards.TAGS.values() for t in ts}
    his |= {f"{p['kind']} · {c.month(p['date'])}" for p in c.POSTS}
    found = {k: v for k, v in found.items() if k not in his}
    for where, items in JS_STRINGS.items():
        for s in items:
            found.setdefault(s, set()).update(where.split())
    rows = []
    for s in sorted(found, key=str.lower):
        rows.append(f"<tr><td>{esc(s)}</td><td>{' '.join(sorted(found[s]))}</td></tr>")
    return len(found), "\n".join(rows)

def build(data):
    cards = []
    for d, name, idea, lines in DIRS:
        built = (OUT / d / "index.html").exists()
        links = " ".join(f'<a href="{d}/{u}">{t}</a>' for u, t in PAGES) if built else "<span>Not built yet</span>"
        rows = "".join(f"<div><dt>{k}</dt><dd>{esc(v)}</dd></div>" for k, v in lines)
        cards.append(f"""<article class="dir{' is-new' if d == 'd' else ''}" id="dir-{d}">
  <a class="dir-shot" href="{d}/" tabindex="-1" aria-hidden="true">{shot(d)}<span class="dir-letter">{d.upper()}</span></a>
  <h2><a href="{d}/">{d.upper()} · {name}</a></h2>
  <p class="idea">{esc(idea)}</p>
  {journey(d) if built else ""}
  <dl>{rows}</dl>
  <p class="open">{links}</p>
</article>""")
    pages, cvs = unlisted()
    n_strings, strings = strings_html()
    page_rows = "".join(f'<li><a href="{u}">{u}</a> <span>{esc(t)}</span></li>' for u, t in public_pages())
    ideas = "".join(f"<li><strong>{esc(t)}</strong>: {esc(why)}</li>" for t, why in CLIP_IDEAS)
    clips = "".join(f"<li><strong>{esc(c.IMAGES[s][1])}</strong> ({esc(c.IMAGES[s][2])})</li>" for s, _ in kit.CLIPS)
    body = f"""<main id="main">
<header class="top">
  <p class="eyebrow">Site redesign · prototypes on the branch claude/site-redesign-26fc25</p>
  <h1>Directions for the new site</h1>
  <p class="lede">Each one is a working homepage, a topic page and an article, made from your real text and pictures. Nothing here is live. Your site stays exactly as it is until you say so.</p>
</header>

<section class="dirs" aria-label="The directions">
{chr(10).join(cards)}
</section>

<section class="ask">
  <h2>What I need from you</h2>
  <ol>
    <li><strong>Look at D</strong>, the mix of A and B, and tell me what to keep or change, however small.</li>
    <li><strong>Choose the clips.</strong> Right now the showcase plays the three clips the site already has. They are only placeholders.</li>
    <li>Then I rebuild the whole site in that direction, on this branch, and show you before anything goes live.</li>
  </ol>
</section>

<details>
  <summary>The clips</summary>
  <p>Playing now, in this order:</p>
  <ul>{clips}</ul>
  <p>Pieces that move, each of which can give a clip exported from its own sketch:</p>
  <ul>{ideas}</ul>
  <p>Beyond the Counted Fields is private, so none of it is used here. Tell me if you want part of it in the showcase.</p>
</details>

<details>
  <summary>What stays the same</summary>
  <ul>
    <li>Every address stays the same: all {len(public_pages())} public pages, the PDFs, sitemap.xml and robots.txt.</li>
    <li>Your words stay as they are, with the alt texts you approved, the page titles and descriptions, the link previews and the structured data.</li>
    <li>Fonts stay on your own site. Nothing loads from other sites.</li>
    <li>The links back to Medium stay.</li>
    <li>The {len(pages)} tailored pages and {len(cvs)} tailored CVs under for/ keep their current look. The new design gets its own files, and I'll ask before changing any of them.</li>
    <li>The build scripts will make the new pages, so importing an article or editing Worlds works as before.</li>
  </ul>
</details>

<details>
  <summary>How these are checked</summary>
  <ul>
    <li><strong>Contrast:</strong> every colour set, in light and dark, is checked by a script for WCAG AA (text at least 4.5 to 1). A page can't take on a colour set that fails.</li>
    <li><strong>Keyboard:</strong> everything can be reached and used with the keyboard, with a visible focus ring. The showcase has pause, previous, next, a choice of clip and the arrow keys. It stops moving on while you read or tab inside it, and while it is off screen.</li>
    <li><strong>Reduced motion:</strong> nothing plays by itself. Colours still change, with a short fade.</li>
    <li><strong>Without JavaScript:</strong> each page reads in one fixed palette, and the showcase shows its first picture with links to the pieces.</li>
    <li><strong>Phones:</strong> checked at 320 and 375 pixels wide: no sideways scrolling, no text under 14 pixels.</li>
    <li><strong>One thing to know about C:</strong> when a room changes between light and dark, the background fades over 0.4 seconds and the text switches halfway. For about a tenth of a second the paler text is below the contrast rule. Everywhere else, and at rest, every page passes.</li>
    <li><strong>One clip at a time:</strong> only the clip on screen loads and plays.</li>
  </ul>
</details>

<details>
  <summary>New words on screen ({n_strings})</summary>
  <p>Words in these prototypes that your site doesn't have now: labels, buttons and names read out by screen readers. Change any of them.</p>
  <table class="strings"><thead><tr><th>Text</th><th>Where</th></tr></thead><tbody>
{strings}
  </tbody></table>
</details>

<details>
  <summary>The audit: today's site</summary>
  <h3>Public pages ({len(public_pages())})</h3>
  <ul class="pages">{page_rows}</ul>
  <p>Not listed anywhere: {len(pages)} tailored pages and {len(cvs)} tailored CVs under /for/. They load the shared assets/site.css, site.js and theme.js, so those three files stay as they are. The {len(c.POSTS)} article sources in _writing/ are not published.</p>
  <h3>How the pages are made</h3>
  <ul>
    <li><strong>build_cards.py</strong>: the 13 projects; the homepage lists 6 of them.</li>
    <li><strong>build_gallery.py</strong>: Worlds (images.html, 106 pieces) and the homepage's 7 Worlds pieces.</li>
    <li><strong>build_blog.py</strong>: each article page from _writing/, the Articles page, the homepage's article lists and sitemap.xml. With --import it first copies new Medium posts.</li>
    <li><strong>build_topics.py</strong>: the four topic pages, the Projects page and the homepage's Research section.</li>
    <li>Written by hand: the CV, the 404 page, and the homepage's opening, publications and contact.</li>
  </ul>
  <h3>The current look</h3>
  <p>Cream paper with a grain over it, Bodoni headings, small uppercase monospace labels, a red seal colour and moss green, a masonry grid in Worlds, and a light and a dark theme. None of the three directions uses any of these.</p>
</details>
</main>"""
    css = """
:root{--bg:#f6f6f4;--fg:#17181a;--fg2:#45474d;--line:#d9d9d4;--card:#fff;--link:#1f4fbf;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#141517;--fg:#f1f1ee;--fg2:#c4c5c9;--line:#34363b;--card:#1d1f22;--link:#9dbbff;color-scheme:dark}}
*{box-sizing:border-box}html{background:var(--bg);color:var(--fg)}
body{margin:0;font:400 1.1875rem/1.6 "Source Serif 4",Georgia,serif;-webkit-font-smoothing:antialiased}
main{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,48px) clamp(16px,4vw,40px) 80px}
a{color:var(--link);text-underline-offset:.2em}a:focus-visible,summary:focus-visible{outline:3px solid var(--link);outline-offset:3px;border-radius:4px}
h1,h2,h3,summary,.eyebrow,dt,.open,.dir-letter,th{font-family:"Space Grotesk",system-ui,sans-serif}
.eyebrow{margin:0 0 .4rem;color:var(--fg2);font-size:1rem}
h1{font-size:clamp(2.2rem,5vw,3.8rem);line-height:1.05;letter-spacing:-.02em;margin:0 0 .4em;font-weight:500}
.lede{font-size:clamp(1.2rem,1.8vw,1.45rem);max-width:46ch;color:var(--fg2);margin:0}
.dirs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:40px 0}
.dir{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px 18px 20px;display:flex;flex-direction:column}
.dir-shot{position:relative;display:block;aspect-ratio:4/3;border-radius:12px;overflow:hidden;background:var(--line);margin-bottom:14px}
.shot{width:100%;height:100%;object-fit:cover;object-position:top}
.dir-letter{position:absolute;left:10px;top:10px;background:var(--fg);color:var(--bg);font-weight:700;font-size:1rem;line-height:1;padding:7px 10px;border-radius:8px}
.dir h2{font-size:1.5rem;font-weight:500;margin:0 0 .25em}.dir h2 a{color:var(--fg);text-decoration:none}.dir h2 a:hover{text-decoration:underline}
.idea{margin:0 0 .8em;font-size:1.15rem}
.journey{list-style:none;display:flex;flex-wrap:wrap;gap:6px;margin:0 0 1em;padding:0}.journey li{font:500 .875rem/1.2 "Space Grotesk",system-ui,sans-serif;padding:6px 10px;border-radius:8px;border:1px solid var(--line)}
.dir dl{margin:0 0 1em;display:grid;gap:10px;flex:1}.dir dt{font-weight:500;font-size:1rem;color:var(--fg2)}.dir dd{margin:0;font-size:1.05rem}
.open{display:flex;flex-wrap:wrap;gap:8px;margin:0}
.open a{display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border-radius:999px;border:1px solid var(--line);text-decoration:none;font-weight:500;font-size:1rem}
.open a:hover{border-color:var(--link)}
.ask{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:8px 24px 14px;margin:0 0 28px}
.ask h2{font-size:1.6rem;font-weight:500}.ask li{margin-bottom:.6em}
details{border-top:1px solid var(--line);padding:6px 0}details:last-of-type{border-bottom:1px solid var(--line)}
summary{cursor:pointer;font-size:1.3rem;font-weight:500;min-height:48px;display:flex;align-items:center}
details[open] summary{margin-bottom:6px}details li{margin-bottom:.35em}
h3{font-size:1.15rem;font-weight:500;margin:1.4em 0 .4em}
.pages{columns:2 360px;padding-left:1.1em;font-size:1rem}.pages span{color:var(--fg2)}
.strings{border-collapse:collapse;width:100%;max-width:820px;font-size:1rem}
.strings th,.strings td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}.strings td+td{white-space:nowrap;color:var(--fg2)}
.skip{position:absolute;left:-9999px;top:8px;padding:.6rem 1rem;background:var(--fg);color:var(--bg);border-radius:8px;z-index:9}.skip:focus{left:8px}
.dir.is-new{grid-column:1/-1;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);column-gap:28px;align-items:start}
.dir.is-new .dir-shot{grid-row:1/span 5;margin-bottom:0}
.dir.is-new h2{font-size:1.9rem}
@media (max-width:980px){.dirs{grid-template-columns:1fr}.dir.is-new{grid-template-columns:1fr}.dir.is-new .dir-shot{grid-row:auto;margin-bottom:14px}}
"""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Directions · site redesign</title>
<meta name="robots" content="noindex">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/seal-32.png">
<link rel="stylesheet" href="shared/fonts.css">
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{body}
</body>
</html>
"""
    kit.write(OUT / "index.html", page)
