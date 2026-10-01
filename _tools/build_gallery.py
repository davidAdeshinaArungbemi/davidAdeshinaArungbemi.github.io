"""Builds images.html and the homepage "Selected images" section from one list.

Run from the repo root:  python3 _tools/build_gallery.py
Each still needs assets/gallery/<slug>-800.jpg and <slug>-1600.jpg (1600 may be
smaller if the source is). Folders starting with "_" are not published by
GitHub Pages, so this script stays out of the live site.
"""
import html, re
from PIL import Image

FB = "https://www.facebook.com/dave.gbemi.98"

# The homepage showcase, in reading order (first row: Water Town, Caustic Bloom, The Art of Intelligence).
SHOWCASE = ["water-town", "stacked-house", "still-life", "caustic-bloom", "calligraphy", "art-of-intelligence", "hard-surface"]

VIDEOS = {
    "water-town": ("assets/video/watertown-loop.mp4", "assets/video/watertown-poster.jpg", 720, 960,
                   "A watercolour water town seen from above; a small sampan rows across the open water past terraced fields and a willow tree."),
    "blender-animation": ("assets/video/blender-animation.mp4", "assets/video/blender-animation-poster.jpg", 960, 540,
                          "A camera moving slowly through a grey, untextured scene of blocks and pillars."),
}

# (slug, title, medium-and-year, caption, alt)   alt is None for videos
GROUPS = [
 ("processing", "Processing · 2026", None, [
  ("water-town", "Water Town", "Processing, 2026", "A watercolour town from above, and one slow morning on it.", None),
  ("ripples", "Ripples", "Processing, 2026", "Water and foam from two equations: interfering waves for the water, and the mathematics of phase separation for the foam.", "Deep teal water patterned with interfering ripples, with white foam gathering into lace at the edges."),
  ("caustic-bloom", "Caustic Bloom", "Processing, 2026", "A flower made only of circles, and never drawn: every circle passes through the centre, and the petals are where they gather.", "A white flower with long petals and a dotted centre, traced by thousands of overlapping circles on black."),
  ("nightbloom", "Nightbloom", "Processing, 2026", "Another flower that is never drawn: a foam whose cells sit on a golden-angle spiral, so the walls between them bloom.", "Pale foam walls on cobalt blue spiralling out from a centre, with a few glossy blue spheres resting among the cells."),
  ("art-of-intelligence", "The Art of Intelligence", "Processing, 2026", "Nine thousand particles combed through a curl-noise field into strands; the hex cascade is the bytes of the poster's own text.", "A poster: bright orange and cyan strands sweep down a black page beside columns of hexadecimal bytes; the title reads 'The Art of Intelligence — David Adeshina'."),
  ("ripples-crab", "Ripples, detail", "Processing, 2026", "Near the crab, every wave takes its shape: the ripples are distances to its outline.", "A close-up of teal ripples curling around the faint shape of a crab."),
  ("poster-variations", "The Art of Intelligence, three earlier versions", "Processing, 2026", "Three different ways of building the same strands.", "Three versions of the same black poster side by side, each with a different sweep of orange and cyan strands."),
  ("prefer-cover", "You Are What You Prefer", "Processing, 2026", "Cover for the essay: a person who exists only as small, benign preferences, with one patch that has quietly changed colour.", "A head in profile made of tiny ink icons of small preferences, beside the title 'You Are What You Prefer'."),
  ("value-tomography", "Value Tomography", "Processing, 2026", "A value system as 144 things and 820 relations. Turned edge-on, each simple question casts a shadow; twelve shadows rebuild the whole.", "Seven frames on black: a tangled chord diagram, lifted into 3D, casting bar-chart shadows, and finally rebuilt in colour."),
  ("value-chords", "Value Chords", "Processing, 2026", "Stories prime values; values predict preferences. All at once it is a tangle.", "A chord diagram titled 'You are what you read': stories on the left, values on top, preferences on the right, joined by coloured ribbons."),
  ("calligraphy", "苏州 · 二〇二六 春", "Processing, 2026", "Procedural brushwork for the Water Town inscription, and the seal that became this site's mark.", "Brush calligraphy reading Suzhou, 2026, Spring, with a red seal reading 雀."),
  ("colour-bird", "Colour Bird", "Processing, 2026", "Feathers fanned like a spectrum; in the sketch, it sways and blinks.", "A cartoon bird perched on a branch, its tail, wing and crest feathers fanned out in rainbow gradients against a starry purple sky."),
 ]),
 ("blender", "3D · Blender", FB, [
  ("island-night", "Island at night", "Blender", "A beach house under a green neon WELCOME sign, among palm trees and sandcastles.", "A small sandy island at night with a wooden beach house glowing under a green neon WELCOME sign, palm trees, sandcastles and beach balls."),
  ("blossom-pond", "Cherry-blossom pond, three views", "Blender", "A low-poly pond under a blossoming tree: by day, from above, and at night.", "Three views of a low-poly rock pond with pink blossoms: a daytime three-quarter view, a top-down view, and a purple night view with glowing petals."),
  ("tea-meringues", "Tea and meringues", "Blender", "A cup of tea with cinnamon sticks and meringues on a saucer.", "A white cup of tea on a saucer with cinnamon sticks, a biscuit and peach-coloured meringues, against a warm brown background."),
  ("robot", "Robot", "Blender", "A small wheeled robot with a camera head and two jointed arms.", "A white and charcoal robot on wheels, with a boxy camera head, two antennae, glowing blue indicators and two jointed arms."),
  ("animal-doughnuts", "Animal doughnuts", "Blender", "A chick, a piglet and a rabbit, as doughnuts.", "Three pale doughnuts on a pink background, decorated as a chick, a piglet and a rabbit."),
  ("glazed-doughnuts", "Glazed doughnuts", "Blender", "Dripping glaze, sprinkles and reflections on a pink floor.", "Three glazed doughnuts with colourful sprinkles, the middle one stacked double, reflected in a glossy pink surface."),
  ("lightsaber", "Lightsaber", "Blender", "A ridged metal hilt with a red blade.", "A lightsaber hilt with a ridged metal grip and a glowing red blade, against a dark background."),
  ("island-night-2", "Island at night, another view", "Blender", "Lit by a single street lamp.", "The same island from another angle, lit by a street lamp and the green neon sign."),
  ("still-life", "Still life with bottles", "Blender", "Glass bottles, a striped ball, boxes and a lettered block on a shelf.", "A blue and a brown glass bottle, a red-and-white striped ball on stacked boxes, a jar and a block with the letter A, on a white shelf."),
  ("three-shapes", "Three shapes in a pool of light", "Blender", "Two cylinders and a cube, in shades of teal.", "Two cylinders and a cube in teal and slate, standing in a soft pool of light on a beige floor."),
  ("cloth-study", "Cloth study", "Blender", "Two red sheets settling over a teal mattress.", "Two red sheets draped over a rounded teal mattress, one sliding off the edge, on a dark blue floor."),
  ("awning-corner", "Corner with an awning", "Blender", "A brick wall, a cloth awning, a barrel, a pot and a mat.", "A low-poly corner scene in muted pinks and browns: a brick wall, a cloth awning on poles, a barrel, a clay pot and a mat."),
  ("stacked-house", "Stacked house", "Blender, 2022", "Modelled from a Pinterest reference, one plank at a time.", "A clay-shaded 3D render of a tall, stacked ramshackle house with a ladder, awnings, a water tank, laundry on a line and a small fenced yard."),
  ("craftsman-house", "Craftsman house", "Blender", "A clay render of a porch house with a tiled roof, in long grass.", "A grey clay render of a single-storey house with a columned porch and a tiled roof, surrounded by long grass."),
  ("bar-kiosk", "Bar kiosk", "Blender", "A clay render of a small street bar, with oil drums by the steps.", "A grey clay render of a narrow street kiosk with a BAR sign on its roof, posters on the counter and oil drums by the steps."),
  ("plug-adapter", "Plug adapter", "Blender", "A product render, lit like a studio shot.", "A white UK plug adapter with metal pins, rendered against a soft grey studio background."),
  ("product-study", "Product study", "Blender", "A white device with a dial, in the same studio light.", "A white L-shaped device with a round dial and a small recessed tray, against a soft grey studio background."),
  ("wonderful-world", "Wonderful World", "Blender, 2024", "A sculpted island of pale stone, with a walkway and railing along its ridge.", "A pale sculpted stone island floating against a soft gradient, with a thin walkway and railing along its top."),
  ("light-study", "Blocks under a spotlight", "Blender, 2022", "Grey and yellow blocks arranged in a ring under a single light.", "Rectangular blocks in grey, black and yellow arranged in a ring under a soft spotlight on a dark floor."),
  ("blender-animation", "Animation exercise", "Blender, 2024", "A camera moving through a grey, untextured scene.", None),
  ("rigging", "Rigging a character, in progress", "Blender", "A low-poly figure with its control rig.", "A Blender window showing a grey low-poly human figure with its control rig and timeline."),
  ("hard-surface", "Hard-surface modelling, in progress", "Blender", "The wireframe of a rugged box with a hinged lid.", "A Blender window showing the wireframe of a rugged, rounded box with screws and hinges on its lid."),
 ]),
 ("earlier", "Earlier experiments", None, [
  ("vector-portrait", "Portrait", "Vector illustration", "A girl with striped pink hair and striped eyes.", "A flat vector portrait of a girl with diagonally striped pink hair, striped teal eyes and round pink cheeks, on a dark background."),
  ("tarot-vae", "Tarot-VAE, generated cards", "Python, 2025", "Cards dreamed up by a small model trained on tarot art, assembled patch by patch.", "A strip of five blurry, patchwork tarot-like cards generated by a neural network."),
  ("vortex-2021", "Untitled", "Code, December 2021", "Thousands of rectangles pulled toward a dark centre. Where it started.", "A monochrome spiral of thousands of small grey rectangles pulling toward a dark centre."),
  ("tunnel-2021", "Untitled", "Code, December 2021", "Zig-zag lines folding into a tunnel.", "A monochrome tunnel of fine zig-zag lines receding to a black centre."),
 ]),
]

def dims(slug, w):
    return Image.open(f"assets/gallery/{slug}-{w}.jpg").size

def img_tag(slug, alt, sizes):
    w8, h8 = dims(slug, 800); w16, _ = dims(slug, 1600)
    srcset = f' srcset="assets/gallery/{slug}-800.jpg {w8}w, assets/gallery/{slug}-1600.jpg {w16}w" sizes="{sizes}"' if w16 > w8 else ""
    return f'<img src="assets/gallery/{slug}-800.jpg"{srcset} alt="{html.escape(alt, quote=True)}" width="{w8}" height="{h8}" loading="lazy">'

def video_tag(slug):
    src, poster, w, h, label = VIDEOS[slug]
    return (f'<video src="{src}" poster="{poster}" style="background: url(\'{poster}\') center / cover" data-inview muted loop '
            f'playsinline preload="none" width="{w}" height="{h}" aria-label="{html.escape(label, quote=True)}"></video>')

def ratio(slug):
    if slug in VIDEOS:
        w, h = VIDEOS[slug][2:4]; return h / w
    w, h = dims(slug, 800); return h / w

def figure_full(slug, title, meta, caption, alt):
    cap = f'<figcaption><strong>{title}</strong> · {meta}. {caption}</figcaption>'
    if slug in VIDEOS:
        return f'        <figure class="g-item" id="{slug}">\n          {video_tag(slug)}\n          {cap}\n        </figure>'
    return (f'        <figure class="g-item" id="{slug}">\n'
            f'          <a class="zoom" href="assets/gallery/{slug}-1600.jpg" aria-label="{html.escape(title, quote=True)}, view full size">'
            f'{img_tag(slug, alt, "(max-width: 760px) 100vw, 540px")}</a>\n'
            f'          {cap}\n        </figure>')

def balanced(items, ncols=2, caption=0.2):
    cols = [[] for _ in range(ncols)]; h = [0.0] * ncols
    for it in items:
        i = h.index(min(h)); cols[i].append(it); h[i] += ratio(it[0]) + caption
    return cols

def build():
    count = sum(len(g[3]) for g in GROUPS)
    sections = []
    for gid, heading, more, items in GROUPS:
        cols = "\n".join('      <div class="gcol">\n' + "\n".join(figure_full(*it) for it in c) + '\n      </div>' for c in balanced(items))
        extra = f'\n  <p class="see-all"><a href="{more}">More of my 3D work on Facebook →</a></p>' if more else ""
        sections.append(f'<section class="images-group" aria-labelledby="h-{gid}">\n  <h2 class="eyebrow" id="h-{gid}">{heading}</h2>\n'
                        f'  <div class="gallery-cols">\n{cols}\n  </div>{extra}\n</section>')
    page = open("images.html", encoding="utf-8").read()
    start = page.index('<section class="images-group"'); end = page.index("</main>")
    page = page[:start] + "\n\n".join(sections) + "\n" + page[end:]
    open("images.html", "w", encoding="utf-8").write(page)

    by = {it[0]: it for g in GROUPS for it in g[3]}
    def medium(slug): return by[slug][2].split(",")[0]
    figs = []
    for slug in SHOWCASE:
        title = by[slug][1]
        inner = video_tag(slug) if slug in VIDEOS else \
            f'<a href="images.html#{slug}">{img_tag(slug, by[slug][4], "(max-width: 640px) 100vw, (max-width: 1100px) 33vw, 352px")}</a>'
        figs.append(f'    <figure class="g-item">\n      {inner}\n      <figcaption><strong>{title}</strong> · {medium(slug)}</figcaption>\n    </figure>')
    section = ('<section class="images" id="images">\n  <h2 class="eyebrow">Selected images</h2>\n'
               "  <p class=\"images-intro\">Worlds that don't exist until someone makes them, in code with Processing and in 3D with Blender.</p>\n"
               '  <div class="gallery">\n' + "\n".join(figs) + '\n  </div>\n'
               f'  <p class="see-all"><a href="images.html">See all {count} images →</a></p>\n</section>')
    home = open("index.html", encoding="utf-8").read()
    home = re.sub(r'<section class="images" id="images">.*?</section>', lambda m: section, home, count=1, flags=re.S)
    open("index.html", "w", encoding="utf-8").write(home)
    print(f"images.html: {count} pieces · homepage showcase: {len(SHOWCASE)}")

if __name__ == "__main__":
    build()
