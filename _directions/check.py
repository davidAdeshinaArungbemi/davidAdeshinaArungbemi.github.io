"""Mechanical checks for the direction prototypes. Run from the repo root:

  python3 _directions/check.py a b c          check these directions
  python3 _directions/check.py --strings a    list text in the prototype that the live site doesn't have
                                              (the new interface strings David needs to review)

For each page of a direction it checks that
  - the HTML nests properly, ids are unique, there is one h1, <html lang>, a <title>, <main id="main">
    and a skip link, and heading levels never jump down by more than one
  - every <img> has an alt attribute, every button and link has a name a screen reader can read
  - every local href/src resolves to a file, and every #anchor to an id on its page
  - the live page's text all appears (his words unchanged and nothing dropped); misses are listed
And it reports the page weight: HTML, CSS, JS, fonts, images that load at once, the first clip.
Exits with 1 when there are errors (warnings don't count).
"""
import html, os, re, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(".").resolve()
HERE = Path(__file__).resolve().parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
PAGES = {"index.html": "index.html",
         "stories-and-ai.html": "stories-and-ai/index.html",
         "the-narrative-hypothesis.html": "articles/the-narrative-hypothesis/index.html"}

class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.kids = tag, dict(attrs), parent, []
        self.line = 0

class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.cur = self.root
        self.problems = []
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        n.line = self.getpos()[0]
        self.cur.kids.append(n)
        if tag not in VOID:
            self.cur = n
    def handle_startendtag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        n.line = self.getpos()[0]
        self.cur.kids.append(n)
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is self.root:
            self.problems.append(f"line {self.getpos()[0]}: stray </{tag}>")
            return
        if n is not self.cur:
            self.problems.append(f"line {self.getpos()[0]}: <{self.cur.tag}> left open inside <{tag}>")
        self.cur = n.parent
    def handle_data(self, data):
        self.cur.kids.append(data)

_cache = {}
def parse(path):
    path = Path(path)
    if path not in _cache:
        t = Tree()
        t.feed(path.read_text(encoding="utf-8"))
        t.close()
        _cache[path] = t
    return _cache[path]

def walk(n):
    for k in n.kids:
        if isinstance(k, Node):
            yield k
            yield from walk(k)

def text(n, skip=("script", "style")):
    out = []
    for k in n.kids:
        if isinstance(k, str):
            out.append(k)
        elif k.tag not in skip:
            out.append(text(k, skip))
    return "".join(out)

def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()

def find(n, tag=None, **attrs):
    for k in walk(n):
        if (tag is None or k.tag == tag) and all(k.attrs.get(a.replace("_", "-")) == v for a, v in attrs.items()):
            return k
    return None

def ids(tree):
    return {k.attrs["id"] for k in walk(tree.root) if "id" in k.attrs} | {k.attrs["name"] for k in walk(tree.root) if k.tag == "a" and "name" in k.attrs}

def exists_exact(path):
    path = Path(path)
    if not path.exists():
        return False
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return True
    here = ROOT
    for part in rel.parts:
        if part not in os.listdir(here):
            return False
        here = here / part
    return True

def resolve(page, url):
    """(file path or None for outside links, fragment)."""
    url = html.unescape(url.strip())
    if not url or re.match(r"^(https?:|mailto:|tel:|data:)", url):
        return None, ""
    if url.startswith("javascript:"):
        return "javascript", ""
    path, _, frag = url.partition("#")
    path = path.split("?")[0]
    if not path:
        return page, frag
    target = ROOT / path.lstrip("/") if path.startswith("/") else page.parent / path
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.resolve(), frag

def spoken(n):
    """Text inside n that assistive tech reads: skips aria-hidden and hidden parts."""
    out = []
    for k in n.kids:
        if isinstance(k, str):
            out.append(k)
        elif k.tag not in ("script", "style") and k.attrs.get("aria-hidden") != "true" and "hidden" not in k.attrs:
            if k.tag == "img":
                out.append(" " + k.attrs.get("alt", "") + " ")
            elif k.tag == "svg":
                out.append(" " + k.attrs.get("aria-label", "") + " ")
            else:
                out.append(spoken(k))
    return "".join(out)

def name_of(n):
    """What a screen reader would call this element (roughly)."""
    if n.attrs.get("aria-label"):
        return n.attrs["aria-label"]
    if n.attrs.get("aria-labelledby"):
        return "(labelledby)"
    return norm(spoken(n)) or n.attrs.get("title", "")

def hidden_from_at(n):
    while n is not None and n.tag != "#root":
        if n.attrs.get("aria-hidden") == "true":
            return True
        n = n.parent
    return False

def check_page(d, page):
    errors, warns = [], []
    tree = parse(page)
    root = tree.root
    for p in tree.problems:
        errors.append(f"nesting: {p}")
    html_el = find(root, "html")
    if not html_el or not html_el.attrs.get("lang"):
        errors.append("no <html lang>")
    if not find(root, "title") or not norm(text(find(root, "title"))):
        errors.append("no <title>")
    if not find(root, "main", id="main"):
        errors.append('no <main id="main">')
    skip = next((k for k in walk(root) if k.tag == "a" and k.attrs.get("href") == "#main"), None)
    if not skip:
        errors.append("no skip link to #main")
    seen = {}
    for k in walk(root):
        if "id" in k.attrs:
            if k.attrs["id"] in seen:
                errors.append(f'duplicate id "{k.attrs["id"]}" (lines {seen[k.attrs["id"]]} and {k.line})')
            seen[k.attrs["id"]] = k.line
    heads = [(int(k.tag[1]), k.line, norm(text(k))[:50]) for k in walk(root) if re.fullmatch(r"h[1-6]", k.tag)]
    if sum(1 for h in heads if h[0] == 1) != 1:
        errors.append(f"{sum(1 for h in heads if h[0] == 1)} h1 elements (want 1)")
    for (a, _, _), (b, line, t) in zip(heads, heads[1:]):
        if b > a + 1:
            warns.append(f"heading jumps h{a} → h{b} at line {line} ({t})")
    for k in walk(root):
        if k.tag == "img" and "alt" not in k.attrs:
            errors.append(f"line {k.line}: <img src={k.attrs.get('src')}> has no alt")
        if k.tag == "img" and not (k.attrs.get("width") and k.attrs.get("height")):
            warns.append(f"line {k.line}: <img src={k.attrs.get('src')}> has no width/height")
        if k.tag == "button" and not name_of(k):
            errors.append(f"line {k.line}: a button with no name")
        if k.tag == "a" and "href" in k.attrs and not hidden_from_at(k) and not name_of(k):
            errors.append(f"line {k.line}: a link with no name ({k.attrs['href']})")
        if k.tag == "video" and not ("muted" in k.attrs and "playsinline" in k.attrs):
            errors.append(f"line {k.line}: <video> without muted and playsinline")
        if k.tag in ("a", "button") and k.attrs.get("tabindex") == "-1" and k.attrs.get("aria-hidden") != "true":
            warns.append(f"line {k.line}: <{k.tag}> taken out of the tab order but not hidden")
    # local links and files
    for k in walk(root):
        for attr in ("href", "src", "poster", "data-src"):
            if attr not in k.attrs or (attr == "href" and k.tag not in ("a", "link")):
                continue
            target, frag = resolve(page, k.attrs[attr])
            if target is None:
                continue
            if target == "javascript":
                errors.append(f"line {k.line}: javascript: link")
                continue
            if not exists_exact(target):
                errors.append(f"line {k.line}: {attr}={k.attrs[attr]} → missing file (or wrong case) {target.relative_to(ROOT) if ROOT in target.parents else target}")
                continue
            if frag and target.suffix == ".html" and not frag.startswith(("t=", ":~:")):
                if frag not in ids(parse(target)):
                    errors.append(f"line {k.line}: {k.attrs[attr]} → no #{frag} on {target.name}")
    for css in sorted(page.parent.glob("*.css")) + sorted((HERE / "shared").glob("*.css")):
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", css.read_text(encoding="utf-8")):
            u = m.group(1)
            if u.startswith(("data:", "#", "http")):
                continue
            target = ROOT / u.lstrip("/") if u.startswith("/") else css.parent / u
            if not target.exists():
                errors.append(f"{css.name}: url({u}) → missing file")
    return errors, warns

def fidelity(page, live):
    """Every sentence of the live page's main text should appear in the prototype."""
    proto = norm(text(parse(page).root))
    live_main = find(parse(live).root, "main")
    misses = []
    for chunk in re.split(r"(?<=[.?!])\s+|\n+", text(live_main)):
        c = norm(chunk)
        if len(c) >= 12 and c not in proto:
            misses.append(c)
    return misses

def weight(page):
    tree = parse(page)
    size = lambda p: p.stat().st_size if p and p != "javascript" and Path(p).exists() else 0
    parts = {"html": page.stat().st_size, "css": 0, "js": 0, "fonts": 0, "images at once": 0, "first clip": 0}
    for k in walk(tree.root):
        if k.tag == "link" and k.attrs.get("rel") == "stylesheet":
            parts["css"] += size(resolve(page, k.attrs["href"])[0])
        if k.tag == "script" and k.attrs.get("src"):
            parts["js"] += size(resolve(page, k.attrs["src"])[0])
        if k.tag == "img" and k.attrs.get("loading") != "lazy" and k.attrs.get("src"):
            parts["images at once"] += size(resolve(page, k.attrs["src"])[0])
    first = next((k for k in walk(tree.root) if "data-slide" in k.attrs), None)
    if first is not None:
        parts["first clip"] = size(resolve(page, first.attrs["data-src"])[0])
    fonts = HERE / "shared" / "fonts.css"
    for m in re.finditer(r"url\(([^)]+)\)", fonts.read_text(encoding="utf-8")):
        u = m.group(1).strip("'\"")
        parts["fonts"] += size(ROOT / u.lstrip("/") if u.startswith("/") else fonts.parent / u)
    return parts

def kb(n): return f"{n / 1024:,.0f} KB"

def new_strings(directions):
    corpus = []
    for live in list(PAGES.values()) + ["cv.html", "projects/index.html", "articles/index.html", "images.html"]:
        t = parse(ROOT / live)
        corpus.append(norm(text(t.root)))
        corpus += [norm(k.attrs[a]) for k in walk(t.root) for a in ("alt", "aria-label", "title") if k.attrs.get(a)]
    corpus = " \n ".join(corpus)
    found = {}
    for d in directions:
        for page in PAGES:
            p = HERE / d / page
            if not p.exists():
                continue
            root = parse(p).root
            for k in walk(root):
                if k.tag in ("script", "style") or "proto" in k.attrs.get("class", "") or k.tag == "title":
                    continue
                for s in [x for x in k.kids if isinstance(x, str)] + [k.attrs.get(a, "") for a in ("aria-label", "title", "alt", "aria-roledescription")]:
                    s = norm(s)
                    if not s or not re.search(r"[A-Za-z]", s) or s in corpus:
                        continue
                    if any(anc.attrs.get("class") == "proto" for anc in [k] + list(_ancestors(k))):
                        continue
                    found.setdefault(s, set()).add(d.upper())
    return found

def _ancestors(n):
    while n.parent is not None:
        n = n.parent
        yield n

def main(args):
    if args and args[0] == "--strings":
        found = new_strings(args[1:] or ["a", "b", "c"])
        for s in sorted(found, key=str.lower):
            print(f"  [{' '.join(sorted(found[s]))}] {s}")
        print(f"{len(found)} strings the live site doesn't have")
        return 0
    bad = 0
    for d in args or ["a", "b", "c"]:
        folder = HERE / d
        if not folder.exists():
            print(f"== {d}: not built")
            continue
        print(f"== direction {d.upper()}")
        for page, live in PAGES.items():
            p = folder / page
            if not p.exists():
                print(f"  {page}: MISSING")
                bad += 1
                continue
            errors, warns = check_page(d, p)
            misses = fidelity(p, ROOT / live)
            w = weight(p)
            status = "ERR" if errors else ("ok, with notes" if warns or misses else "ok")
            print(f"  {page}: {status}   " + " · ".join(f"{k} {kb(v)}" for k, v in w.items() if v))
            for e in errors:
                print(f"    ERROR  {e}")
            for wn in warns:
                print(f"    note   {wn}")
            for m in misses:
                print(f"    text   not found: {m[:110]}")
            bad += bool(errors)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
