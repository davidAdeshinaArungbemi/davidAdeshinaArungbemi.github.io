"""One row in a plain list: a small picture, a label, a title, one line, topic tags and extra links.
Projects, articles and the topic pages all use it (build_cards.py, build_blog.py, build_topics.py),
so every list on the site looks the same. Links and images come out site-absolute ("/assets/...").
"""
import html
from PIL import Image

esc = lambda s: html.escape(s, quote=False)
attr = lambda s: html.escape(s, quote=True)

def absolute(u):
    return u if u.startswith(("http://", "https://", "/", "#", "mailto:")) else "/" + u

def row(link, img, kind, title, line, tags=(), extras=(), group=None):
    link, img = absolute(link), absolute(img)
    w, h = Image.open(img.lstrip("/")).size
    data = f' data-kind="{group}"' if group else ""
    tag_html = ('\n        <ul class="card-tags">' + "".join(f"<li>{esc(t)}</li>" for t in tags) + "</ul>") if tags else ""
    extra_html = ('\n        <p class="row-extra">' + "".join(f'<a href="{attr(absolute(u))}">{esc(t)}</a>' for t, u in extras)
                  + "</p>") if extras else ""
    return (f'    <li class="row"{data}>\n'
            f'      <a class="row-thumb" href="{attr(link)}" tabindex="-1" aria-hidden="true">'
            f'<img src="{attr(img)}" alt="" width="{w}" height="{h}" loading="lazy"></a>\n'
            f'      <div class="row-text">\n'
            f'        <p class="row-kind">{esc(kind)}</p>\n'
            f'        <h3 class="row-title"><a href="{attr(link)}">{esc(title)}</a></h3>\n'
            f'        <p class="row-line">{esc(line)}</p>{tag_html}{extra_html}\n'
            f'      </div>\n'
            f'    </li>')

NAV = [("Research", "/#research"), ("Publications", "/#publications"), ("Articles", "/articles/"),
       ("Projects", "/projects/"), ("Worlds", "/images.html"), ("CV", "/cv.html"), ("Contact", "/#contact")]

def nav(current=None):
    """The top navigation; `current` is the label of the page being shown, if it's one of them."""
    return "\n".join(f'    <a href="{u}"' + (' aria-current="page"' if t == current else "") + f">{t}</a>" for t, u in NAV)
