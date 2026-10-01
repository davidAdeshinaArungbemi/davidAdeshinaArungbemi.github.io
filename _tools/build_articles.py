"""Refreshes the homepage article list from the Medium feed.

Run from the repo root:  python3 _tools/build_articles.py
Lists the N most recent articles, leaving out the one featured above the list.
"""
import email.utils, html, re, urllib.request

FEED = "https://medium.com/feed/@suzume1"
FEATURED = "dream-a-better-dream"     # shown as the selected article, so not repeated in the list
N = 6

def fetch():
    req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (Macintosh)"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

def articles(xml):
    out = []
    for it in re.findall(r"<item>(.*?)</item>", xml, re.S):
        title = html.unescape(re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", it, re.S).group(1)).strip()
        link = re.search(r"<link>(.*?)</link>", it).group(1).split("?")[0]
        date = email.utils.parsedate_to_datetime(re.search(r"<pubDate>(.*?)</pubDate>", it).group(1))
        if FEATURED not in link:
            out.append((date, title, link))
    return sorted(out, reverse=True)[:N]

def build():
    rows = articles(fetch())
    lis = "\n".join(f'    <li><a href="{link}"><span class="date">{date.strftime("%b %Y")}</span>'
                    f'<span class="title">{html.escape(title)}</span></a></li>' for date, title, link in rows)
    page = open("index.html", encoding="utf-8").read()
    page, n = re.subn(r'(<ol class="articles">).*?(</ol>)', lambda m: f"{m.group(1)}\n{lis}\n  {m.group(2)}", page, count=1, flags=re.S)
    assert n == 1, "article list not found in index.html"
    open("index.html", "w", encoding="utf-8").write(page)
    print(f"articles: {len(rows)} listed")

if __name__ == "__main__":
    build()
