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
    "caustic-bloom": "A flower made only of circles, each passing through the centre.",
    "gyronics-axol": "A wearable I designed for Gyronics: a hexagonal unit that glows green, on interchangeable bands.",
    "art-of-intelligence": "Nine thousand particles swept into strands, beside the poster's own words written in hexadecimal.",
    "calligraphy": "Procedural brushwork, and the seal that became this site's mark.",
    "hard-surface": "The wireframe of a rugged box with a hinged lid.",
    "stacked-house": "Modelled from a Pinterest reference, one plank at a time.",
    "still-life": "Glass bottles, a striped ball and a lettered block on a shelf.",
}

VIDEOS = {
    "robot-arm": ("assets/video/robot-arm.mp4", "assets/video/robot-arm-poster.jpg", 1280, 792,
                  "A screen recording of Blender: a jointed robot arm on a grey floor picks up a small cube while a Python script runs beside it."),
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
  ("caustic-bloom", "Caustic Bloom", "Processing, 2026", "A flower made only of circles. Every circle passes through the centre, and the petals appear where the circles crowd together.", "A white flower with long petals and a dotted centre, traced by thousands of overlapping circles on black."),
  ("nightbloom", "Nightbloom", "Processing, 2026", "A foam whose cells sit on a golden-angle spiral, so the walls between them form a flower.", "Pale foam walls on cobalt blue spiralling out from a centre, with a few glossy blue spheres resting among the cells."),
  ("art-of-intelligence", "The Art of Intelligence", "Processing, 2026", "Nine thousand particles carried along a swirling flow field (curl noise) until they form strands. The columns of hexadecimal down the side are the poster's own text, byte by byte.", "A poster: bright orange and cyan strands sweep down a black page beside columns of hexadecimal bytes; the title reads 'The Art of Intelligence — David Adeshina'."),
  ("ripples-crab", "Ripples, detail", "Processing, 2026", "Close up, the ripples curve around a faint crab. Each ring follows its outline at a growing distance, like contour lines on a map.", "A close-up of teal ripples curling around the faint shape of a crab."),
  ("poster-variations", "The Art of Intelligence, three earlier versions", "Processing, 2026", "Three different ways of building the same strands.", "Three versions of the same black poster side by side, each with a different sweep of orange and cyan strands."),
  ("prefer-cover", "You Are What You Prefer", "Processing, 2026", "Cover for the essay: a person who exists only as small, benign preferences, with one patch that has quietly changed colour.", "A head in profile made of tiny ink icons of small preferences, beside the title 'You Are What You Prefer'."),
  ("value-tomography", "Value Tomography", "Processing, 2026", "A value system drawn as 144 things and 820 links, too tangled to read from above. Turned on its side, its shadow on the wall becomes a bar chart: the answer to one simple question. Twelve questions give twelve shadows, and together they come close to the whole.", "Seven frames on black: a tangled chord diagram, lifted into 3D, casting bar-chart shadows, and finally rebuilt in colour."),
  ("value-chords", "Value Chords", "Processing, 2026", "Stories lead to values, and values lead to preferences, all drawn as one ring of ribbons. In the sketch, clicking any node lights up only its path. The weights are placeholders for now.", "A chord diagram titled 'You are what you read': stories on the left, values on top, preferences on the right, joined by coloured ribbons."),
  ("calligraphy", "苏州 · 二〇二六 春", "Processing, 2026", "Procedural brushwork for the Water Town inscription, and the seal that became this site's mark.", "Brush calligraphy reading Suzhou, 2026, Spring, with a red seal reading 雀."),
  ("colour-bird", "Colour Bird", "Processing, 2026", "Feathers fanned like a spectrum; in the sketch, it sways and blinks.", "A cartoon bird perched on a branch, its tail, wing and crest feathers fanned out in rainbow gradients against a starry purple sky."),
 ]),
 ("blender", "3D · Blender", FB, [
  ("gyronics-axol", "Axol, a wearable for Gyronics", "Blender, 2025", "A design I made for Gyronics, the assistive-technology startup I co-founded: a hexagonal compute unit that glows green, on interchangeable bands. This is a render of the design; teammates built the physical prototypes.", "Three renders of the Axol wearable on black: a black woven band whose hexagonal top glows green, with two more bands angled on either side."),
  ("gyronics-concept-2024", "First concept for the Gyronics wearable", "Blender, 2024", "My first design for Gyronics, from May 2024: a dark band with a glass-like top and the Gyronics name glowing on it. A render of the design, before Axol.", "A black wearable band with a curved, glass-like top showing the glowing word Gyronics, and two small status lights on its side, on a dark background."),
  ("gyronics-hex-pink", "Hexagon wearable, pink band", "Blender, 2024", "A design I made for Gyronics in December 2024: a hexagonal unit with a soft white light, on a perforated pink band. A render of the design.", "A pink perforated wristband with a glowing white hexagonal unit, on a dark surface."),
  ("gyronics-hex-wrist", "Hexagon wearable, on the wrist", "Blender, 2024", "The same Gyronics design in black, shown on a modelled wrist. A render of the design.", "A black wristband with a glowing white hexagonal unit, worn on a smooth modelled forearm."),
  ("gyronics-hex-copper", "Hexagon wearable, copper pads", "Blender, 2025", "A later version for Gyronics, January 2025: a glowing green hexagon on a woven black band with copper pads. A render of the design.", "A black woven wristband with a glowing green hexagonal unit and copper pads, lit from above."),
  ("gyronics-square-2025", "Square wearable concept", "Blender, 2025", "Another concept for Gyronics, March 2025: a square unit with a green cube on its face and a row of green lights, on a knitted grey band. A render of the design.", "A square wearable on a grey knitted band, with a glowing green cube on its screen and a row of small green lights."),
  ("island-night", "Island at night", "Blender", "A beach house under a green neon WELCOME sign, among palm trees and sandcastles.", "A small sandy island at night with a wooden beach house glowing under a green neon WELCOME sign, palm trees, sandcastles and beach balls."),
  ("blossom-pond", "Cherry-blossom pond, three views", "Blender", "A low-poly pond under a blossoming tree: by day, from above, and at night.", "Three views of a low-poly rock pond with pink blossoms: a daytime three-quarter view, a top-down view, and a purple night view with glowing petals."),
  ("tea-meringues", "Tea and meringues", "Blender", "A cup of tea with cinnamon sticks and meringues on a saucer.", "A white cup of tea on a saucer with cinnamon sticks, a biscuit and peach-coloured meringues, against a warm brown background."),
  ("robot", "Robot", "Blender, 2024", "A small wheeled robot with a camera head and two jointed arms.", "A white and charcoal robot on wheels, with a boxy camera head, two antennae, glowing blue indicators and two jointed arms."),
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
  ("rigging", "Rigging a character, in progress", "Blender, 2024", "A low-poly figure with its control rig.", "A Blender window showing a grey low-poly human figure with its control rig and timeline."),
  ("robot-arm", "Robot arm, moved by a script", "Blender and Python, 2025", "A robot arm rigged in Blender and moved by a Python script inside it: the arm turns, reaches a cube, picks it up and lets it go.", None),
  ("santa-hat", "Santa hat", "Blender, 2022", "A soft red Santa hat with a furry trim and pompom.", "A red Santa hat with a thick grey fur trim and a fluffy pompom, on a warm brown background."),
  ("hard-surface", "Hard-surface modelling, in progress", "Blender", "The wireframe of a rugged box with a hinged lid.", "A Blender window showing the wireframe of a rugged, rounded box with screws and hinges on its lid."),
 ]),
 ("drawing", "Sketches & paintings", None, [
  # Newest first: 2022, then paintings and sketches without a date (screenshots from Aug 2023), then 2021, then 2020
  ("vector-portrait", "Portrait", "Vector illustration, 2022", "A girl with striped pink hair and striped eyes.", "A flat vector portrait of a girl with diagonally striped pink hair, striped teal eyes and round pink cheeks, on a dark background."),
  ("pencil-studies-2022", "Pencil studies", "Pencil, 2022", "An eye, lips, a profile and a full face, drawn in early 2022.", "Four pencil studies on paper: an eye, a pair of lips, a woman in profile and a woman's face from the front."),
  ("desert-2022", "Desert", "Vector illustration, June 2022", "Layered dunes and cacti under a pale sun, in shades of terracotta.", "A flat vector desert: rolling terracotta dunes in layers, dotted with cacti, under a large pale sun."),
  ("vector-sunflower-2022", "Sunflower", "Vector illustration, October 2022", "A giant sunflower over a pine forest and a blue sky.", "A flat vector illustration of a tall yellow sunflower above dark green pine trees, with white clouds on a bright blue sky."),
  ("vector-moon-2022", "Moon and stars", "Vector illustration, December 2022", "A full moon and scattered stars over a calm, dark sea.", "A flat vector night scene: a white full moon and small stars above a dark blue sea."),
  ("vector-sunset-2022", "Sunset", "Vector illustration, July 2022", "A red sun breaking up on the water.", "A flat vector sunset: a coral-red sun split into jagged pieces on grey-blue water."),
  ("vector-hills-2022", "Hills", "Vector illustration, July 2022", "Green hills, white clouds and dark rocks.", "A flat vector landscape of green and brown hills under a pale blue sky with clouds, dark rocks in front."),
  ("vector-face-2022", "Face", "Vector illustration, July 2022", "A girl with purple hair and a single tear.", "A flat vector girl with purple hair and a blue tear on her cheek, on a dark red background."),
  ("vector-fish-2022", "Weird fish", "Vector illustration, August 2022", "A navy fish with a pink stripe.", "A flat vector fish in navy blue with a pink stripe and a white eye, on black."),
  ("eye-study-2022", "Eye study", "Pencil, February 2022", "A shaded eye, with a face sketched in the corner.", "A pencil drawing of a heavily shaded eye on grey paper, with a small face sketched at the top."),
  ("red-skirt-2022", "Girl in a red skirt", "Digital drawing, February 2022", "A girl with long hair in a red skirt and white blouse, with petals falling around her.", "A coloured drawing of a girl with long brown hair, a white blouse and a red pleated skirt, with red petals around her."),
  ("face-guidelines-2022", "Face with guidelines", "Pencil, February 2022", "A man’s face measured out with guidelines.", "A pencil drawing of a man’s face with construction lines across it."),
  ("face-shaded-2022", "Face study, shaded", "Pencil, March 2022", "A woman’s face built up in cross-hatching.", "A pencil drawing of a woman’s face, shaded with dense cross-hatching."),
  ("hoop-earrings-2022", "Hoop earrings", "Pencil, April 2022", "A woman with curly hair and hoop earrings.", "A pencil drawing of a woman with short curly hair and large hoop earrings."),
  ("face-study-2022", "Face study", "Pencil, April 2022", "A woman’s face with its guidelines still showing.", "A pencil drawing of a woman’s face with faint guidelines and hatching."),
  ("ink-plants-2022", "Wolf under a tree", "Ink, June 2022", "A wolf and a tree in black silhouette under a hatched moon, with loose studies of leaves around them.", "A black ink drawing of a wolf standing under a tree, with a cross-hatched moon behind and small leaf studies around the page."),
  ("chibi-faces-2022", "Chibi faces", "Pencil, June 2022", "A page of small, round cartoon faces.", "A sketchbook page of small round cartoon faces with big eyes."),
  ("round-face-2022", "Round face", "Pencil, June 2022", "A simple, round girl’s face with big hair.", "A simple pencil drawing of a round-faced girl with big hair."),
  ("cat-window", "Cat at the window", "Digital painting", "A cat watching bare trees through a bright window, in shades of grey.", "A greyscale painting of a black and white cat on a windowsill, looking out at bare trees."),
  ("night-walk", "Night walk", "Digital painting", "A girl in headphones walks past a full moon and a falling comet, her bag glowing teal.", "A girl in a hoodie and headphones walks along a railing at night under a huge full moon and a comet."),
  ("black-cat", "Black cat", "Digital painting", "A black cat against bright light, painted in black and white.", "A black cat silhouetted against a white background, with soft grey highlights."),
  ("man-scarf", "Man in a scarf", "Digital sketch", "A man with long hair and a scarf, in loose lines.", "A loose grey line sketch of a man with long hair and a scarf, seen from the side."),
  ("umbrella", "Under one umbrella", "Digital sketch", "Two people sharing an umbrella.", "An ink-style sketch of two people standing close together under one umbrella."),
  ("head-sketch", "Head study", "Digital sketch", "A man’s head in quick, searching lines.", "A quick line sketch of a man’s head and shoulders."),
  ("woman-jacket", "Woman in a jacket", "Digital sketch", "A woman with her hair up, in an open jacket.", "A line sketch of a woman with her hair up, wearing an open jacket."),
  ("horned-figure", "Horned figure", "Digital painting", "A horned character in grey tones, lit from behind.", "A greyscale painting of a horned character standing against a bright, misty background."),
  ("swordfighter", "Swordfighter", "Digital sketch", "A fighter raising a sword, in rough lines.", "A rough line sketch of a figure raising a sword over another figure."),
  ("standing-girl", "Standing girl", "Digital sketch", "A girl with a fringe, standing with one knee bent.", "A light line sketch of a girl with a fringe, standing with one knee bent."),
  # 2021 digital paintings and sketches
  ("skull-2021", "Skull", "Digital painting, 2021", "A skull resting on dark, misty ground.", "A digitally painted skull on a dark grey, misty surface."),
  ("sphere-and-book", "Sphere and book", "Digital painting, 2021", "A sphere on a bronze stand, and the shadow it throws on a red book.", "A cream sphere on an ornate bronze stand with claw feet, in front of a standing maroon book, on a dark table against a dark wall."),
  ("banana-on-cloth", "Banana on a cloth", "Digital painting, 2021", "A bruised banana on a folded cloth.", "A ripe yellow banana with small brown bruises lying on a folded grey-green cloth on a grey-violet surface."),
  ("staff-2021", "Character with a staff", "Digital painting, 2021", "An oversized jumper, hair over one eye, and a staff that ends in twig fingers.", "A figure with long auburn hair falling over one eye, wearing an oversized blue-grey jumper, baggy olive trousers and black boots, holding a tall staff topped with twig-like fingers, against a turquoise sky and green foliage."),
  ("head-study-2021", "Head study", "Digital painting, 2021", "An early try at a face, turned three-quarters.", "A painted head of a person with long crimson hair, thick dark brows and red lips, turned three-quarters against a pale blue background."),
  ("sword-cap-2021", "Figure with a sword", "Sketch, June 2021", "A woman in a cap and uniform, holding a sword.", "A light sketch of a woman in a peaked cap and uniform, holding a sword."),
  ("hair-up-2021", "Hair pinned up", "Sketch, June 2021", "A woman’s face in bold lines, her hair pinned up.", "A bold line drawing of a woman’s face with her hair pinned up."),
  ("bun-2021", "Girl with a bun", "Sketch, June 2021", "A girl with a ribboned bun, in light lines.", "A light line sketch of a girl with a bun tied with a ribbon."),
  ("dance-2021", "Dance", "Sketch, June 2021", "A man mid-dance, one knee raised.", "A line sketch of a man dancing with one knee raised and arms out."),
  ("twin-tails-2021", "Twin tails", "Sketch, June 2021", "A girl with long twin tails and a bow.", "A line sketch of a girl with long twin tails and a bow."),
  ("leap-2021", "Leap", "Sketch, June 2021", "A figure leaping, beside two smaller studies of the pose.", "A line sketch of a figure leaping with a raised arm, with two small pose studies beside it."),
  ("box-2021", "Box", "Sketch, June 2021", "A storage box with its lid lifted.", "A simple line drawing of a storage box with its lid raised."),
  ("ribbons-2021", "Girl with ribbons", "Sketch, June 2021", "A girl with long hair and ribbons, in faint lines.", "A faint sketch of a girl with long hair and ribbons."),
  ("still-life-2021", "Jug, bottle and bowl", "Sketch, June 2021", "A still life of a jug, a bottle and a bowl.", "A line drawing of a jug, a tall bottle and a bowl."),
  ("standing-2021", "Standing figure", "Sketch, June 2021", "A woman standing with her hands on her hips.", "A line sketch of a woman standing with her hands on her hips."),
  ("bob-2021", "Girl with a bob", "Sketch, June 2021", "A girl with a bob, glancing to the side.", "A line sketch of a girl with a bob haircut glancing sideways."),
  ("guidelines-2021", "Face on guidelines", "Sketch, June 2021", "A face built on construction lines, on yellow.", "A sketch of a woman’s face with construction lines, on a pale yellow background."),
  ("seated-2021", "Seated figure", "Sketch, June 2021", "A woman sitting with one knee up.", "A line sketch of a woman sitting with one knee raised."),
  ("hands-face-2021", "Hands to face", "Sketch, June 2021", "A girl holding her hands to her face.", "A small, light sketch of a girl holding her hands to her face."),
  ("short-hair-2021", "Girl with short hair", "Sketch, June 2021", "A girl with short hair, in faint lines.", "A faint line sketch of a girl with short hair."),
  ("reach-2021", "Reaching", "Sketch, June 2021", "A woman stretching one arm up.", "A line sketch of a woman stretching one arm above her head."),
  ("gestures-2021", "Gesture studies", "Sketch, June 2021", "Quick gesture figures in blue.", "A page of quick blue gesture sketches of small figures in motion."),
  ("arms-crossed-2021", "Arms crossed", "Sketch, June 2021", "A boy with messy hair and crossed arms.", "A line sketch of a boy with messy hair and his arms crossed."),
  ("bold-face-2021", "Bold face", "Sketch, June 2021", "A woman’s face in heavy, confident lines.", "A heavy black line drawing of a woman’s face."),
  ("startled-2021", "Startled", "Sketch, June 2021", "A girl with long hair and wide, startled eyes.", "A line sketch of a girl with long hair and wide, startled eyes."),
  ("dress-2021", "Girl in a dress", "Sketch, June 2021", "A girl standing in a strapless dress.", "A light line sketch of a girl standing in a strapless dress."),
  # 2020: the earliest drawings on the drive
  ("spiky-hair-2020", "Girl with spiky hair", "Pencil, May 2020", "A girl’s head with short, spiky hair.", "A pencil drawing of a girl’s head with short spiky hair, on grey paper."),
  ("long-hair-2020", "Girl with long hair", "Pencil, June 2020", "A girl with long, straight hair, shaded in pencil.", "A shaded pencil drawing of a girl with long straight hair."),
  ("lined-paper-2020", "On lined paper", "Pencil, June 2020", "A girl with her hair tied back, drawn on lined paper.", "A faint pencil drawing of a girl with tied-back hair on lined notebook paper."),
 ]),
 ("earlier", "Earlier experiments", None, [
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

def ordered():
    """Interleave Processing and Blender so the first rows mix both; then sketches and paintings; earlier experiments last."""
    by = {gid: items for gid, _, _, items in GROUPS}
    p, b = by["processing"], by["blender"]
    out = []
    for i in range(max(len(p), len(b))):
        if i < len(p): out.append(("processing", p[i]))
        if i < len(b): out.append(("blender", b[i]))
    return out + [("drawing", it) for it in by["drawing"]] + [("earlier", it) for it in by["earlier"]]

def year_tag(meta):
    """A small year tag under the caption, when the medium-and-year field has a year."""
    m = re.search(r"(19|20)\d\d", meta)
    return f'<ul class="card-tags"><li>{m.group(0)}</li></ul>' if m else ""

def pin_full(kind, it):
    slug, title, meta, caption, alt = it
    cap = (f'<figcaption><strong>{title}</strong><span class="pin-meta"> · {meta}. </span>'
           f'<span class="pin-desc">{caption}</span>{year_tag(meta)}</figcaption>')
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
            '    <button type="button" data-filter="drawing" aria-pressed="false">Sketches &amp; paintings</button>\n'
            '    <button type="button" data-filter="earlier" aria-pressed="false">Earlier experiments</button>\n'
            '  </div>')
    main = ('<main id="main">\n<section class="page-head">\n  <h1>Worlds</h1>\n'
            "  <p>Things that don't exist until someone makes them: Processing sketches written with Claude as a pair-programmer, "
            "scenes in Blender, drawings and paintings, and the experiments where it started. Select any image to see it full size.</p>\n"
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
        _, title, meta, caption, alt = by[slug]
        media = (f'<div class="pin-media">{video_tag(slug)}</div>' if slug in VIDEOS else
                 f'<a class="pin-media" href="images.html#{slug}">{img_tag(slug, alt, "(max-width: 640px) 50vw, (max-width: 1100px) 50vw, 360px")}</a>')
        pins.append(f'    <figure class="pin">\n      {media}\n      <figcaption><strong>{title}</strong>'
                    f'<span class="pin-desc">{SHORT.get(slug, caption)}</span>{year_tag(meta)}</figcaption>\n    </figure>')
    section = ('<section class="images" id="worlds">\n  <h2 class="eyebrow">Worlds</h2>\n'
               "  <p class=\"images-intro\">Things that don't exist until someone makes them, in code with Processing, in 3D with Blender, and by hand.</p>\n"
               '  <div class="pins" data-min="280">\n' + "\n".join(pins) + '\n  </div>\n'
               f'  <p class="see-all"><a href="images.html">See all {count} pieces →</a></p>\n</section>')
    home = open("index.html", encoding="utf-8").read()
    home = re.sub(r'<section class="images" id="[a-z]+">.*?</section>', lambda m: section, home, count=1, flags=re.S)
    open("index.html", "w", encoding="utf-8").write(home)
    print(f"images.html: {count} pieces · homepage Worlds: {len(SHOWCASE)}")

if __name__ == "__main__":
    build()
