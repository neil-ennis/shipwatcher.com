"""Check that the generated prototype covers the catalog and old post IDs."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
if sys.argv[1:] not in ([], ["--site"]):
    raise SystemExit("Usage: python check.py [--site]")
DIST = ROOT / ("site" if "--site" in sys.argv[1:] else "dist")
ships = json.loads((ROOT / "data" / "ships.json").read_text(encoding="utf-8"))
active = [ship for ship in ships if ship.get("active", True)]
historical = [ship for ship in ships if not ship.get("active", True)]


class LocalLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paths: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        value = attr.get({"a": "href", "link": "href", "script": "src", "img": "src"}.get(tag, ""))
        if value and value.startswith("/"):
            self.paths.append(urlsplit(value).path)


expected = {str(s["legacy_post_id"]): f"/{s['slug']}/" for s in ships if s["legacy_post_id"] is not None}
generated = json.loads((DIST / "postmap.json").read_text(encoding="utf-8"))
assert generated == expected, "Generated shortlink map does not match the catalog"
original_shortlinks = json.loads((ROOT / "legacy" / "postmap.json").read_text(encoding="utf-8"))
assert all(generated.get(post_id) == path for post_id, path in original_shortlinks.items()), "An original shortlink changed"
assert len(original_shortlinks) == 23, "Original shortlink fixture was altered"
assert (DIST / "ships.json").exists()

for page in [DIST / "index.html", DIST / "about" / "index.html", DIST / "contact" / "index.html", *(DIST / s["slug"] / "index.html" for s in ships)]:
    assert page.exists(), f"Missing page: {page}"
    content = page.read_text(encoding="utf-8")
    assert "<h1" in content and "WordPress" not in content, f"Unexpected page content: {page}"
    if page.parent.name in {ship["slug"] for ship in ships}:
        page_id = "/" + page.parent.name + "/"
        assert f'page-id="{page_id}"' in content and '<comentario-comments theme="light"' in content, f"Missing preserved comments: {page}"
    links = LocalLinks()
    links.feed(content)
    for path in links.paths:
        target = DIST / path.lstrip("/")
        if path.endswith("/"):
            target /= "index.html"
        assert target.is_file(), f"Broken local path {path} in {page}"

index = (DIST / "index.html").read_text(encoding="utf-8")
assert index.count('data-ship-card') == len(active)
for ship in historical:
    assert f'data-name="{ship["name"].lower()}"' not in index
    page = (DIST / ship["slug"] / "index.html").read_text(encoding="utf-8")
    assert "Former camera listing" in page and 'data-camera-image' not in page
assert index.count('"source": "https://') == 5, "Approved quotes or source links are missing"
assert "A window onto" not in index
assert "https://blog.neilennis.com/contact/" in (DIST / "contact" / "index.html").read_text(encoding="utf-8")
assert (DIST / "404.html").is_file() and (DIST / "feed.xml").is_file()
assert (DIST / "sitemap.xml").read_text(encoding="utf-8").count("<url>") == len(active) + 3
assert "/category/p-o-australia/ / 301" in (DIST / "_redirects").read_text(encoding="utf-8")
print(f"Checked {len(ships)} catalog entries, ship pages, local links and legacy post IDs")
