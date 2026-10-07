"""Builds the Worlds page (images.html) and the homepage Worlds section from one list.

Run from the repo root:  python3 _tools/build_gallery.py
Each still needs assets/gallery/<slug>-800.jpg and <slug>-1600.jpg (the 1600 may be
smaller if the source is). Folders starting with "_" are not published by
GitHub Pages, so this script stays out of the live site.
"""
import html, re
from PIL import Image

FB = "https://www.facebook.com/dave.gbemi.98"

# The homepage showcase, in reading order (pins fill the shortest column, Pinterest-style).
SHOWCASE = ["blossom-pond", "water-town", "caustic-bloom", "gyronics-axol", "art-of-intelligence", "calligraphy", "hard-surface", "stacked-house", "still-life"]

# Shorter descriptions for the homepage; anything not listed uses its full caption.
SHORT = {
    "water-town": "A watercolour town from above, and one slow morning on it.",
    "caustic-bloom": "A flower made only of circles, and never drawn.",
    "gyronics-axol": "A wearable I designed for Gyronics: a hexagonal unit that glows green, on interchangeable bands.",
    "art-of-intelligence": "Nine thousand particles combed into strands; the hex is the poster's own text.",
    "calligraphy": "Procedural brushwork, and the seal that became this site's mark.",
    "hard-surface": "The wireframe of a rugged box with a hinged lid.",
    "stacked-house": "Modelled from a Pinterest reference, one plank at a time.",
    "still-life": "Glass bottles, a striped ball and a lettered block on a shelf.",
}

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
  ("gyronics-axol", "Axol, a wearable for Gyronics", "Blender, 2025", "A design I made for Gyronics, the assistive-technology startup I co-founded: a hexagonal compute unit that glows green, on interchangeable bands. This is a render of the design; teammates built the physical prototypes.", "Three renders of the Axol wearable on black: a black woven band whose hexagonal top glows green, with two more bands angled on either side."),
  ("gyronics-concept-2024", "First concept for the Gyronics wearable", "Blender, 2024", "My first design for Gyronics, from May 2024: a dark band with a glass-like top and the Gyronics name glowing on it. A render of the design, before Axol.", "A black wearable band with a curved, glass-like top showing the glowing word Gyronics, and two small status lights on its side, on a dark background."),
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
  # 2021 digital paintings: here for whoever looks closely, never in the homepage showcase
  ("sphere-and-book", "Sphere and book", "Digital painting, 2021", "A sphere on a bronze stand, and the shadow it throws on a red book.", "A cream sphere on an ornate bronze stand with claw feet, in front of a standing maroon book, on a dark table against a dark wall."),
  ("banana-on-cloth", "Banana on a cloth", "Digital painting, 2021", "A bruised banana on a folded cloth.", "A ripe yellow banana with small brown bruises lying on a folded grey-green cloth on a grey-violet surface."),
  ("staff-2021", "Character with a staff", "Digital painting, 2021", "An oversized jumper, hair over one eye, and a staff that ends in twig fingers.", "A figure with long auburn hair falling over one eye, wearing an oversized blue-grey jumper, baggy olive trousers and black boots, holding a tall staff topped with twig-like fingers, against a turquoise sky and green foliage."),
  ("head-study-2021", "Head study", "Digital painting, 2021", "An early try at a face, turned three-quarters.", "A painted head of a person with long crimson hair, thick dark brows and red lips, turned three-quarters against a pale blue background."),
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

def ordered():
    """Interleave Processing and Blender so the first rows mix both; earlier experiments last."""
    by = {gid: items for gid, _, _, items in GROUPS}
    p, b = by["processing"], by["blender"]
    out = []
    for i in range(max(len(p), len(b))):
        if i < len(p): out.append(("processing", p[i]))
        if i < len(b): out.append(("blender", b[i]))
    return out + [("earlier", it) for it in by["earlier"]]

def pin_full(kind, it):
    slug, title, meta, caption, alt = it
    cap = (f'<figcaption><strong>{title}</strong><span class="pin-meta"> · {meta}. </span>'
           f'<span class="pin-desc">{caption}</span></figcaption>')
    if slug in VIDEOS:
        media = f'<div class="pin-media">{video_tag(slug)}</div>'
    else:
        media = (f'<a class="pin-media zoom" href="assets/gallery/{slug}-1600.jpg" aria-label="{html.escape(title, quote=True)}, view full size">'
                 f'{img_tag(slug, alt, "(max-width: 640px) 50vw, (max-width: 1100px) 33vw, 270px")}</a>')
    return f'    <figure class="pin" id="{slug}" data-kind="{kind}">\n      {media}\n      {cap}\n    </figure>'

def build():
    items = ordered(); count = len(items)
    tabs = ('  <div class="pin-tabs" role="group" aria-label="Show">\n'
            '    <button type="button" data-filter="all" aria-pressed="true">All</button>\n'
            '    <button type="button" data-filter="processing" aria-pressed="false">Processing</button>\n'
            '    <button type="button" data-filter="blender" aria-pressed="false">3D · Blender</button>\n'
            '    <button type="button" data-filter="earlier" aria-pressed="false">Earlier experiments</button>\n'
            '  </div>')
    main = ('<main id="main">\n<section class="page-head">\n  <h1>Worlds</h1>\n'
            "  <p>Things that don't exist until someone makes them: Processing sketches written with Claude as a pair-programmer, "
            "scenes in Blender, and the experiments where it started. Select any image to see it full size.</p>\n"
            f'{tabs}\n</section>\n\n<section class="images-all" aria-label="All pieces">\n  <div class="pins" data-min="220" data-filterable>\n'
            + "\n".join(pin_full(k, it) for k, it in items) +
            f'\n  </div>\n  <p class="see-all"><a href="{FB}">More of my 3D work on Facebook →</a></p>\n</section>\n</main>')
    page = open("images.html", encoding="utf-8").read()
    page = re.sub(r"<main id=\"main\">.*?</main>", lambda m: main, page, count=1, flags=re.S)
    page = re.sub(r"<title>.*?</title>", "<title>Worlds · David Adeshina Arungbemi</title>", page, count=1)
    open("images.html", "w", encoding="utf-8").write(page)

    by = {it[0]: it for _, it in items}
    pins = []
    for slug in SHOWCASE:
        _, title, _, caption, alt = by[slug]
        media = (f'<div class="pin-media">{video_tag(slug)}</div>' if slug in VIDEOS else
                 f'<a class="pin-media" href="images.html#{slug}">{img_tag(slug, alt, "(max-width: 640px) 50vw, (max-width: 1100px) 50vw, 360px")}</a>')
        pins.append(f'    <figure class="pin">\n      {media}\n      <figcaption><strong>{title}</strong>'
                    f'<span class="pin-desc">{SHORT.get(slug, caption)}</span></figcaption>\n    </figure>')
    section = ('<section class="images" id="worlds">\n  <h2 class="eyebrow">Worlds</h2>\n'
               "  <p class=\"images-intro\">Things that don't exist until someone makes them, in code with Processing and in 3D with Blender.</p>\n"
               '  <div class="pins" data-min="280">\n' + "\n".join(pins) + '\n  </div>\n'
               f'  <p class="see-all"><a href="images.html">See all {count} pieces →</a></p>\n</section>')
    home = open("index.html", encoding="utf-8").read()
    home = re.sub(r'<section class="images" id="[a-z]+">.*?</section>', lambda m: section, home, count=1, flags=re.S)
    open("index.html", "w", encoding="utf-8").write(home)
    print(f"images.html: {count} pieces · homepage Worlds: {len(SHOWCASE)}")

if __name__ == "__main__":
    build()
