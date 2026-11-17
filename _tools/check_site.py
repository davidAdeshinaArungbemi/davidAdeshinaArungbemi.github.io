"""Checks the built site. Run from the repo root after a build:

  python3 _tools/check_site.py            check every public page against itself and against the same page on main
  python3 _tools/check_site.py --base REF compare with another git ref instead of main

For every public page:
  - the HTML nests properly; ids are unique; one h1; <html lang>, a <title>, <main id="main"> and a skip link;
    heading levels never jump down by more than one
  - every <img> has alt, width and height; every button and link has a name a screen reader can read
  - every local href/src resolves to a file with exactly that name (GitHub Pages is case-sensitive), and every
    #anchor to an id on its page; the unlisted for/ pages' links into the site are checked too
  - nothing is fetched from another site (fonts, scripts, styles), and no page loads the old assets/site.css
  - compared with the base ref: every sentence of the old page's text is still there, every alt text, and every
    title, description, canonical, Open Graph, Twitter and JSON-LD line is unchanged
Then the homepage's weight and sitemap.xml are reported. Exits 1 on errors (notes don't count).
"""
import html, os, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(".").resolve()
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

def public_pages():
    pages = ["index.html", "cv.html", "images.html", "404.html", "articles/index.html", "projects/index.html"]
    pages += sorted(str(p) for p in Path("articles").glob("*/index.html"))
    pages += [f"{t}/index.html" for t in ("stories-and-ai", "aesthetics", "visualisation", "minds")]
    return pages

class Node:
    def __init__(self, tag, attrs, parent, line=0):
        self.tag, self.attrs, self.parent, self.kids, self.line = tag, dict(attrs), parent, [], line

class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.cur, self.problems = self.root, []
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur, self.getpos()[0])
        self.cur.kids.append(n)
        if tag not in VOID:
            self.cur = n
    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, attrs, self.cur, self.getpos()[0]))
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
def parse_text(key, text):
    if key not in _cache:
        t = Tree(); t.feed(text); t.close()
        _cache[key] = t
    return _cache[key]

def parse(path):
    return parse_text(str(Path(path).resolve()), Path(path).read_text(encoding="utf-8"))

def walk(n):
    for k in n.kids:
        if isinstance(k, Node):
            yield k
            yield from walk(k)

def text(n):
    return "".join(k if isinstance(k, str) else ("" if k.tag in ("script", "style") else text(k)) for k in n.kids)

def spaced(n):
    """The text with a space at every element boundary, as a reader sees separate pieces."""
    return " ".join(k if isinstance(k, str) else ("" if k.tag in ("script", "style") else spaced(k)) for k in n.kids)

def strings(n):
    """Every text node under n, outside scripts and styles."""
    for k in n.kids:
        if isinstance(k, str):
            if k.strip(): yield k
        elif k.tag not in ("script", "style"):
            yield from strings(k)

def spoken(n):
    out = []
    for k in n.kids:
        if isinstance(k, str):
            out.append(k)
        elif k.tag not in ("script", "style") and k.attrs.get("aria-hidden") != "true" and "hidden" not in k.attrs:
            out.append(" " + (k.attrs.get("alt", "") if k.tag == "img" else k.attrs.get("aria-label", "") if k.tag == "svg" else spoken(k)) + " ")
    return "".join(out)

def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()

def name_of(n):
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

def ids_of(tree):
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
    url = html.unescape(url.strip())
    if not url or re.match(r"^(https?:|mailto:|tel:|data:)", url):
        return None, ""
    if url.startswith("javascript:"):
        return "javascript", ""
    path, _, frag = url.partition("#")
    path = path.split("?")[0]
    if not path:
        return Path(page).resolve(), frag
    target = ROOT / path.lstrip("/") if path.startswith("/") else Path(page).parent / path
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.resolve(), frag

def link_errors(page, tree):
    errors = []
    for k in walk(tree.root):
        for a in ("href", "src", "poster", "data-src", "srcset"):
            if a not in k.attrs or (a == "href" and k.tag not in ("a", "link")):
                continue
            urls = [u.strip().split(" ")[0] for u in k.attrs[a].split(",")] if a == "srcset" else [k.attrs[a]]
            for u in urls:
                target, frag = resolve(page, u)
                if target is None:
                    continue
                if target == "javascript":
                    errors.append(f"line {k.line}: javascript: link")
                elif not exists_exact(target):
                    errors.append(f"line {k.line}: {a}={u} → no such file")
                elif frag and target.suffix == ".html" and not frag.startswith(("t=", ":~:", "lens=")) and frag not in ids_of(parse(target)):
                    errors.append(f"line {k.line}: {u} → no #{frag} on {target.relative_to(ROOT)}")
    return errors

def check_page(page):
    errors, notes = [], []
    tree = parse(page)
    root = tree.root
    errors += [f"nesting: {p}" for p in tree.problems]
    h = next((k for k in walk(root) if k.tag == "html"), None)
    if not h or not h.attrs.get("lang"): errors.append("no <html lang>")
    if not any(k.tag == "title" and norm(text(k)) for k in walk(root)): errors.append("no <title>")
    if not any(k.tag == "main" and k.attrs.get("id") == "main" for k in walk(root)): errors.append('no <main id="main">')
    if not any(k.tag == "a" and k.attrs.get("href") == "#main" for k in walk(root)): errors.append("no skip link")
    seen = {}
    for k in walk(root):
        if "id" in k.attrs:
            if k.attrs["id"] in seen: errors.append(f'duplicate id "{k.attrs["id"]}"')
            seen[k.attrs["id"]] = k.line
    heads = [(int(k.tag[1]), k.line, norm(text(k))[:50]) for k in walk(root) if re.fullmatch(r"h[1-6]", k.tag)]
    if sum(1 for x in heads if x[0] == 1) != 1: errors.append(f"{sum(1 for x in heads if x[0] == 1)} h1 elements")
    for (a, _, _), (b, line, t) in zip(heads, heads[1:]):
        if b > a + 1: notes.append(f"heading jumps h{a} → h{b} at line {line} ({t})")
    for k in walk(root):
        if k.tag == "img" and "alt" not in k.attrs: errors.append(f"line {k.line}: img without alt ({k.attrs.get('src')})")
        if k.tag == "img" and not (k.attrs.get("width") and k.attrs.get("height")): notes.append(f"line {k.line}: img without width/height ({k.attrs.get('src')})")
        if k.tag == "button" and not name_of(k): errors.append(f"line {k.line}: button without a name")
        if k.tag == "a" and "href" in k.attrs and not hidden_from_at(k) and not name_of(k): errors.append(f"line {k.line}: link without a name ({k.attrs['href']})")
        if k.tag == "video" and not ("muted" in k.attrs and "playsinline" in k.attrs): errors.append(f"line {k.line}: video without muted and playsinline")
        if k.tag in ("link", "script") and re.match(r"https?://", k.attrs.get("href", k.attrs.get("src", "")) or ""):
            if not (k.tag == "link" and k.attrs.get("rel") in ("canonical", "alternate")):
                errors.append(f"line {k.line}: <{k.tag}> fetched from another site")
        if k.tag == "link" and k.attrs.get("href", "").lstrip("/") == "assets/site.css": errors.append("loads the old assets/site.css")
    errors += link_errors(page, tree)
    return errors, notes

def base_text(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def head_lines(page_html):
    head = re.search(r"<head>(.*?)</head>", page_html, re.S)
    out = set()
    for line in (head.group(1) if head else "").splitlines():
        s = line.strip()
        if (s.startswith("<title>") or s.startswith('<script type="application/ld+json">') or s.startswith('<link rel="canonical"')
                or re.match(r'<meta (name="(description|robots|twitter:[a-z]+)"|property="(og|article):[a-z_:]+")', s)):
            out.add(s)
    return out

def compare(page, ref):
    """What the base ref's version of this page had that the new one lost."""
    old = base_text(ref, page)
    if old is None:
        return ["(not on the base ref)"]
    new = Path(page).read_text(encoding="utf-8")
    lost = []
    for line in sorted(head_lines(old) - head_lines(new)):
        lost.append(f"head line: {line[:140]}")
    told = parse_text(f"{ref}:{page}", old).root
    tnew = parse(page).root
    main_old = next((k for k in walk(told) if k.tag == "main"), told)
    # Each piece of the old text (every text node, split into sentences) must appear in the new page with the same
    # words in the same order. Punctuation between separate elements, like the old " · " joins, doesn't count.
    words = lambda s: re.findall(r"[\w’']+", s.lower())
    new_words = " " + " ".join(words(spaced(tnew))) + " "
    for node in strings(main_old):
        for chunk in re.split(r"(?<=[.?!])\s+", node):
            c = norm(chunk)
            if len(c) >= 12 and " " + " ".join(words(c)) + " " not in new_words:
                lost.append(f"text: {c[:120]}")
    new_alts = {norm(k.attrs.get("alt", "")) for k in walk(tnew) if k.tag == "img"} | {norm(k.attrs.get("aria-label", "")) for k in walk(tnew)}
    for k in walk(told):
        if k.tag == "img" and norm(k.attrs.get("alt", "")) and norm(k.attrs["alt"]) not in new_alts:
            lost.append(f"alt: {k.attrs['alt'][:120]}")
    return lost

def weight(page):
    tree = parse(page)
    size = lambda p: Path(p).stat().st_size if p and p != "javascript" and Path(p).exists() else 0
    parts = {"html": Path(page).stat().st_size, "css": 0, "js": 0, "fonts": 0, "images at once": 0, "first clip": 0}
    for k in walk(tree.root):
        if k.tag == "link" and k.attrs.get("rel") == "stylesheet": parts["css"] += size(resolve(page, k.attrs["href"])[0])
        if k.tag == "script" and k.attrs.get("src"): parts["js"] += size(resolve(page, k.attrs["src"])[0])
        if k.tag == "img" and k.attrs.get("loading") != "lazy" and k.attrs.get("src"): parts["images at once"] += size(resolve(page, k.attrs["src"])[0])
    first = next((k for k in walk(tree.root) if "data-slide" in k.attrs), None)
    if first is not None: parts["first clip"] = size(resolve(page, first.attrs["data-src"])[0])
    for f in ("space-grotesk-400", "space-grotesk-500", "space-grotesk-700", "source-serif-4"):
        parts["fonts"] += size(f"assets/fonts/{f}.woff2")
    return parts

def main(argv):
    ref = argv[argv.index("--base") + 1] if "--base" in argv else "main"
    bad = 0
    for page in public_pages():
        errors, notes = check_page(page)
        lost = compare(page, ref)
        status = "ERR" if errors else ("ok, with notes" if notes or lost else "ok")
        print(f"{page}: {status}")
        for e in errors: print(f"    ERROR  {e}")
        for n in notes: print(f"    note   {n}")
        for l in lost: print(f"    lost?  {l}")
        bad += bool(errors)
    for page in sorted(str(p) for p in Path("for").glob("**/index.html")):
        errs = [e for e in link_errors(page, parse(page))]
        if errs:
            print(f"{page}: links")
            for e in errs: print(f"    ERROR  {e}")
            bad += 1
    sm = Path("sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>https://davidadeshinaarungbemi\.github\.io(/[^<]*)</loc>", sm)
    missing = [u for u in locs if not exists_exact(resolve("index.html", u)[0])]
    print(f"sitemap.xml: {len(locs)} pages" + (f", missing: {missing}" if missing else ", all present") + (", lists for/!" if any("/for/" in u for u in locs) else ""))
    bad += bool(missing)
    w = weight("index.html")
    print("homepage weight: " + " · ".join(f"{k} {v / 1024:,.0f} KB" for k, v in w.items()) + f" · total {sum(w.values()) / 1024:,.0f} KB")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
