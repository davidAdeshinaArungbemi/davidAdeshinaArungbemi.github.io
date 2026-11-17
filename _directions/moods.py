"""Colour for the three design directions.

A "mood" is a small set of colours taken from one picture: the page (or one card) wears them while
that picture is the thing being shown, pointed at or scrolled to. Every mood is built with fixed
lightness steps, so text keeps WCAG AA contrast whatever the hue, and build.py checks each one.

  analyse(path)        -> the picture's key hue, second hue, how colourful it is, how light it is
  palette(a, scheme)   -> the token colours for one direction and scheme, as hex
  contrast(hex, hex)   -> WCAG contrast ratio
"""
import math
from functools import lru_cache
from PIL import Image

# ---------------------------------------------------------------- OKLab / OKLCH <-> sRGB

def _lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def _gam(c): return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

def rgb_to_oklab(r, g, b):
    r, g, b = _lin(r), _lin(g), _lin(b)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)

def oklab_to_rgb(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (+4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

def _in_gamut(rgb, eps=1e-4): return all(-eps <= c <= 1 + eps for c in rgb)

def hexcol(L, C, h):
    """OKLCH -> sRGB hex. Out-of-gamut colours lose chroma, never lightness or hue."""
    L = min(1.0, max(0.0, L))
    hr = math.radians(h)
    lo, hi = 0.0, max(0.0, C)
    rgb = oklab_to_rgb(L, hi * math.cos(hr), hi * math.sin(hr))
    if not _in_gamut(rgb):
        for _ in range(24):
            mid = (lo + hi) / 2
            if _in_gamut(oklab_to_rgb(L, mid * math.cos(hr), mid * math.sin(hr))): lo = mid
            else: hi = mid
        rgb = oklab_to_rgb(L, lo * math.cos(hr), lo * math.sin(hr))
    return "#" + "".join(f"{round(255 * _gam(min(1, max(0, c)))):02X}" for c in rgb)

def luminance(hx):
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def readable(L, C, h, grounds, want=4.6, step=-0.01):
    """Move lightness one way (step < 0 darker, > 0 lighter) until the colour clears `want` on every ground."""
    for _ in range(80):
        hx = hexcol(L, C, h)
        if all(contrast(hx, g) >= want for g in grounds): return hx
        L += step
    raise ValueError(f"no readable colour at hue {h:.0f} on {grounds}")

# ---------------------------------------------------------------- reading a picture

@lru_cache(maxsize=None)
def analyse(path):
    """Read one picture.
      h      the hue that stands out (a thin red line on cream counts: it is what the eye goes to)
      h2     a second hue, at least 60 degrees away, or a near neighbour when there is none
      s      0..1, how much of the picture is coloured: this tints the ground
      v      0..1, how vivid the standout colour is: this colours links, controls and glow
      light  mean lightness 0..1
    Paper cream and charcoal count as no colour, so those pictures give calm greys."""
    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((96, 96))
        px = list(im.getdata())
    n = len(px)
    bins = [0.0] * 36
    light = spread = 0.0
    vivid = []
    for r, g, b in px:
        L, a, bb = rgb_to_oklab(r / 255, g / 255, b / 255)
        C = math.hypot(a, bb)
        light += L
        spread += max(0.0, C - 0.04)
        if C > 0.06:
            vivid.append(C)
            bins[int((math.degrees(math.atan2(bb, a)) % 360) // 10) % 36] += C ** 1.6
    light /= n
    if len(vivid) < max(6, 0.003 * n):                  # a grey picture: no hue of its own
        return dict(h=250.0, h2=250.0, s=0.0, v=0.0, light=light)
    vivid.sort()
    smooth = [bins[i - 1] * 0.5 + bins[i] + bins[(i + 1) % 36] * 0.5 for i in range(36)]
    def centre(i):                                      # weighted hue around the peak bin
        x = y = 0.0
        for k in (-1, 0, 1):
            w = bins[(i + k) % 36]; ang = math.radians(((i + k) % 36) * 10 + 5)
            x += w * math.cos(ang); y += w * math.sin(ang)
        return math.degrees(math.atan2(y, x)) % 360
    i1 = max(range(36), key=lambda i: smooth[i])
    far = [i for i in range(36) if min((i - i1) % 36, (i1 - i) % 36) >= 6]
    i2 = max(far, key=lambda i: smooth[i])
    h1 = centre(i1)
    h2 = centre(i2) if smooth[i2] > 0.22 * smooth[i1] else (h1 + 28) % 360
    s = min(1.0, (spread / n) / 0.05)
    v = min(1.0, max(0.25, (vivid[int(len(vivid) * 0.9)] - 0.05) / 0.11))
    return dict(h=h1, h2=h2, s=s, v=max(v, s), light=light)

def fixed(h, s=1.0, h2=None, light=0.6, v=None):
    """A mood chosen by hand (the four research topics, the default)."""
    return dict(h=float(h), h2=float(h2 if h2 is not None else (h + 28) % 360), s=s, v=s if v is None else v, light=light)

# ---------------------------------------------------------------- token recipes

def dark_tokens(a):
    h, h2, s, v = a["h"], a["h2"], a["s"], a["v"]
    g = (s + v) / 2
    ground = hexcol(0.172, 0.010 + 0.030 * s, h)
    ground2 = hexcol(0.228, 0.014 + 0.036 * s, h)
    ground3 = hexcol(0.292, 0.018 + 0.050 * s, h)
    on = [ground, ground2, ground3]
    return {
        "ground": ground, "ground-2": ground2, "ground-3": ground3,
        "ink": readable(0.955, 0.012, h, on, 11.0, +0.005),
        "ink-2": readable(0.80, 0.018 + 0.022 * s, h, on, 4.8, +0.01),
        "line": hexcol(0.40, 0.02 + 0.04 * s, h),
        "accent": readable(0.84, 0.03 + 0.115 * v, h, on, 4.8, +0.01),
        "accent-2": readable(0.82, 0.03 + 0.11 * v, h2, on, 4.8, +0.01),
        "on-accent": hexcol(0.17, 0.03, h),
        "glow": hexcol(0.60, 0.02 + 0.16 * g, h),
        "glow-2": hexcol(0.50, 0.02 + 0.15 * g, h2),
    }

def light_tokens(a):
    h, h2, s, v = a["h"], a["h2"], a["s"], a["v"]
    g = (s + v) / 2
    ground = hexcol(0.972, 0.005 + 0.017 * s, h)
    ground2 = hexcol(0.936, 0.008 + 0.032 * s, h)
    ground3 = hexcol(0.888, 0.012 + 0.056 * s, h)
    on = [ground, ground2, ground3]
    return {
        "ground": ground, "ground-2": ground2, "ground-3": ground3,
        "ink": readable(0.215, 0.015 + 0.02 * s, h, on, 11.0, -0.005),
        "ink-2": readable(0.41, 0.02 + 0.03 * s, h, on, 4.8, -0.01),
        "line": hexcol(0.80, 0.02 + 0.05 * s, h),
        "accent": readable(0.47, 0.03 + 0.13 * v, h, on, 4.8, -0.01),
        "accent-2": readable(0.49, 0.03 + 0.12 * v, h2, on, 4.8, -0.01),
        "on-accent": hexcol(0.985, 0.008, h),
        "glow": hexcol(0.84, 0.02 + 0.13 * g, h),
        "glow-2": hexcol(0.87, 0.02 + 0.11 * g, h2),
    }

def palette(a, scheme):
    return dark_tokens(a) if scheme == "dark" else light_tokens(a)

# Pairs that carry text, with the ratio each must reach (WCAG AA: 4.5 body text).
TEXT_PAIRS = [("ink", "ground", 7.0), ("ink", "ground-2", 7.0), ("ink", "ground-3", 7.0),
              ("ink-2", "ground", 4.5), ("ink-2", "ground-2", 4.5), ("ink-2", "ground-3", 4.5),
              ("accent", "ground", 4.5), ("accent", "ground-2", 4.5), ("accent", "ground-3", 4.5),
              ("accent-2", "ground", 4.5), ("accent-2", "ground-2", 4.5),
              ("on-accent", "accent", 4.5)]

def check(tokens, name=""):
    """Raise if any text pair in this palette misses its ratio; return the lowest ratio found."""
    worst = 99.0
    for fg, bg, want in TEXT_PAIRS:
        ratio = contrast(tokens[fg], tokens[bg])
        worst = min(worst, ratio)
        if ratio < want:
            raise AssertionError(f"{name}: {fg} on {bg} is {ratio:.2f}, wants {want}")
    return worst
