"""Take a one-time, public-only snapshot of shipwatcher.com.

The local WordPress installation contained backdoors, so this script never
starts it or reads its database. It only retrieves public pages and the few
same-origin browser assets they reference. Run against a fresh destination.
"""

from __future__ import annotations

import concurrent.futures
import html
from html.parser import HTMLParser
from pathlib import Path
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


ORIGIN = "https://shipwatcher.com"
SITEMAP_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()),
)
USER_AGENT = "ShipWatcher public static archive export/1.0"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        urllib.parse.urljoin(ORIGIN, url), headers={"User-Agent": USER_AGENT}
    )
    try:
        with OPENER.open(request, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError(f"Unexpected status {response.status}: {url}")
            return response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404 and url == "/static-export-missing-page/":
            return error.read()
        raise


def public_paths() -> list[str]:
    root = ET.fromstring(fetch("/wp-sitemap.xml"))
    # WordPress omits archive pagination from its sitemap.
    paths = {
        "/", "/page/2/", "/page/3/", "/author/neilennis/",
        "/author/neilennis/page/2/", "/author/neilennis/page/3/",
        "/category/princess-cruises/page/2/",
    }
    for location in root.findall(".//s:sitemap/s:loc", SITEMAP_NS):
        feed = ET.fromstring(fetch(location.text or ""))
        for item in feed.findall(".//s:url/s:loc", SITEMAP_NS):
            url = urllib.parse.urljoin(ORIGIN, item.text or "")
            parsed = urllib.parse.urlparse(url)
            if parsed.netloc != "shipwatcher.com" or not parsed.path.endswith("/"):
                raise RuntimeError(f"Unexpected sitemap URL: {url}")
            paths.add(parsed.path)
    return sorted(paths)


def remove_balanced_div(markup: str, start_pattern: str) -> str:
    match = re.search(start_pattern, markup, flags=re.I)
    if not match:
        return markup
    start = match.start()
    depth = 0
    for tag in re.finditer(r"</?div\b[^>]*>", markup[start:], flags=re.I):
        depth += -1 if tag.group().lower().startswith("</") else 1
        if depth == 0:
            return markup[:start] + markup[start + tag.end() :]
    raise RuntimeError("Unbalanced WordPress comments block")


def prepare_html(path: str, raw: bytes) -> tuple[str, str | None]:
    markup = raw.decode("utf-8", "replace")
    if "<html" not in markup.lower():
        raise RuntimeError(f"No HTML page at {path}")

    if path == "/" or path.startswith("/page/"):
        markup = markup.replace(
            '<h1 class="wp-block-heading has-text-align-left">Blog</h1>',
            '<h1 class="wp-block-heading has-text-align-left">All Web Cams</h1>',
        )

    if path == "/404.html":
        markup = re.sub(
            r"<main\b[^>]*>.*?</main>",
            '<main class="wp-block-group has-global-padding is-layout-constrained" '
            'style="min-height:45vh;padding:5rem 1rem">'
            '<h1>Page not found</h1><p>That page is not in the ShipWatcher archive. '
            '<a href="/">Return to the home page</a>.</p></main>',
            markup,
            count=1,
            flags=re.I | re.S,
        )
        markup = re.sub(r"<title>.*?</title>", "<title>Page not found – ShipWatcher.com</title>", markup, count=1, flags=re.I | re.S)
        markup = markup.replace("</head>", '<meta name="robots" content="noindex">\n</head>', 1)

    shortlink = re.search(r'<link\b[^>]*rel="shortlink"[^>]*href="/\?p=(\d+)"', markup)
    post_id = shortlink.group(1) if shortlink else None
    if post_id:
        markup = remove_balanced_div(markup, r'<div\b[^>]*class="[^"]*wp-block-comments\b')
        comments = (
            '<section class="ship-comments" aria-label="Comments">'
            '<h2>Comments</h2>'
            '<comentario-comments theme="light" '
            'domain-id="52efca07-e8eb-4711-8e66-83acaa93a8dd" '
            f'page-id="{html.escape(path, quote=True)}">'
            '</comentario-comments></section>'
        )
        markup = markup.replace("</main>", comments + "</main>", 1)
        markup = markup.replace(
            "</head>",
            '<script defer src="https://comments.neilennis.com/comentario.js"></script>\n</head>',
            1,
        )

    # WordPress's sample footer links all point to '#'. Remove the two menus,
    # retaining the site title and existing attribution.
    footer_start = re.search(r"<footer\b", markup, flags=re.I)
    if footer_start:
        prefix, footer = markup[: footer_start.start()], markup[footer_start.start() :]
        footer = re.sub(r"<nav\b[^>]*>.*?</nav>", "", footer, flags=re.I | re.S)
        markup = prefix + footer

    markup = re.sub(r'<link\b[^>]*href="/wp-json/[^\"]*"[^>]*>', "", markup, flags=re.I)
    markup = re.sub(r'<link\b[^>]*href="/xmlrpc\.php[^\"]*"[^>]*>', "", markup, flags=re.I)
    markup = re.sub(r'<link\b[^>]*rel="alternate"[^>]*type="application/rss\+xml"[^>]*>', "", markup, flags=re.I)
    markup = re.sub(r'<script\b[^>]*src="/wp-(?:includes/js/comment-reply|content/plugins/akismet/)[^\"]*"[^>]*>\s*</script>', "", markup, flags=re.I)
    markup = re.sub(r'<link\b[^>]*rel="shortlink"[^>]*>', "", markup, flags=re.I)

    # Keep public canonical URLs for indexing, while all navigation and local
    # assets in the preview use its own hostname.
    protected: list[str] = []

    def hold(match: re.Match[str]) -> str:
        protected.append(match.group())
        return f"__SHIPWATCHER_CANONICAL_{len(protected)-1}__"

    markup = re.sub(
        r'<(?:link|meta)\b[^>]*(?:rel="canonical"|property="og:url")[^>]*>',
        hold,
        markup,
        flags=re.I,
    )
    markup = re.sub(r"https?://shipwatcher\.com(?=/|[\"'\s<]|$)", "", markup, flags=re.I)
    for number, tag in enumerate(protected):
        markup = markup.replace(f"__SHIPWATCHER_CANONICAL_{number}__", tag)

    # Old HTTP webcam URLs would be mixed content on an HTTPS static site.
    markup = re.sub(r"http://(www\.princess\.com|media\.pocruises\.com\.au)/", r"https://\1/", markup, flags=re.I)
    # Pacific Explorer's original webcam image incorrectly linked to Pacific Aria.
    markup = markup.replace(
        '<a href="/pacific-aria/"><img decoding="async" id="webcam116"',
        '<a href="/pacific-explorer/"><img decoding="async" id="webcam116"',
    )
    markup = markup.replace("</head>", '<link rel="stylesheet" href="/shipwatcher.css">\n<script defer src="/shipwatcher.js"></script>\n</head>', 1)
    if path == "/":
        markup = markup.replace("</head>", '<link rel="alternate" type="application/rss+xml" title="ShipWatcher feed" href="/feed.xml">\n</head>', 1)
    return markup, post_id


class AssetRefs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src", "poster"} and value:
                self.refs.add(value)


def asset_paths(markup: str) -> set[str]:
    parser = AssetRefs()
    parser.feed(markup)
    refs = parser.refs | set(re.findall(r'["\'](/wp-(?:content|includes)/[^"\']+\.(?:js|css|woff2?|svg|png|jpg|ico)(?:\?[^"\']*)?)["\']', markup, re.I))
    result = set()
    for ref in refs:
        parsed = urllib.parse.urlparse(urllib.parse.urljoin(ORIGIN, ref))
        if parsed.netloc == "shipwatcher.com" and parsed.path.startswith(("/wp-content/", "/wp-includes/")):
            result.add(parsed.path)
    return result


def main(destination: Path) -> None:
    if destination.exists():
        raise SystemExit(f"Destination exists: {destination}")
    paths = public_paths()
    if len(paths) < 25:
        raise RuntimeError(f"Incomplete sitemap: only {len(paths)} paths")
    destination.mkdir(parents=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        pages = list(pool.map(lambda path: (path, fetch(path)), paths))
    pages.append(("/404.html", fetch("/static-export-missing-page/")))

    postmap: dict[str, str] = {}
    assets: set[str] = set()
    for path, raw in pages:
        markup, post_id = prepare_html(path, raw)
        if post_id:
            postmap[post_id] = path
        target = destination / (path.lstrip("/") + "index.html" if path != "/404.html" else "404.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markup, encoding="utf-8")
        assets |= asset_paths(markup)

    for asset in sorted(assets):
        target = destination / asset.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(fetch(asset))

    from json import dumps

    (destination / "postmap.json").write_text(dumps(postmap, indent=2) + "\n", encoding="utf-8")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{ORIGIN}{path}</loc></url>\n" for path in paths)
    sitemap += "</urlset>\n"
    (destination / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (destination / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://shipwatcher.com/sitemap.xml\n", encoding="utf-8")
    feed = fetch("/feed/")
    if b"<rss" not in feed[:1000]:
        raise RuntimeError("Expected WordPress RSS feed")
    (destination / "feed.xml").write_bytes(feed)
    (destination / "_redirects").write_text("/feed/ /feed.xml 301\n/wp-sitemap.xml /sitemap.xml 301\n", encoding="utf-8")
    for asset in ("shipwatcher.css", "shipwatcher.js"):
        (destination / asset).write_bytes((Path(__file__).parent.parent / "site" / asset).read_bytes())
    print(f"Exported {len(pages)} HTML pages, {len(assets)} same-origin assets, {len(postmap)} post IDs to {destination}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python export_public.py FRESH_DESTINATION")
    main(Path(sys.argv[1]).resolve())
