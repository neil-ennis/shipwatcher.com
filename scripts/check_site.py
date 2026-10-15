"""Check that the exported public site has its required pages and local assets."""

from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlparse, unquote


SITE = Path(__file__).resolve().parents[1] / "site"


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src", "poster"} and value:
                self.refs.append(value)


def main():
    pages = sorted(SITE.rglob("*.html"))
    posts = []
    checked = 0
    missing = []
    for page in pages:
        markup = page.read_text(encoding="utf-8")
        if "<comentario-comments" in markup:
            posts.append(page)
            expected_id = "/" + page.parent.relative_to(SITE).as_posix() + "/"
            if f'page-id="{expected_id}"' not in markup:
                missing.append(f"{page}: wrong Comentario page-id")
        parser = References()
        parser.feed(markup)
        for ref in parser.refs:
            parsed = urlparse(ref)
            if parsed.netloc or not parsed.path.startswith("/"):
                continue
            checked += 1
            target = SITE / unquote(parsed.path.lstrip("/"))
            if parsed.path.endswith("/"):
                target /= "index.html"
            if not target.exists():
                missing.append(f"{page}: {ref}")

    postmap = json.loads((SITE / "postmap.json").read_text(encoding="utf-8"))
    if len(posts) != 23 or len(postmap) != 23:
        missing.append(f"Expected 23 ship pages and shortlinks, found {len(posts)} and {len(postmap)}")
    for post_id, path in postmap.items():
        if not post_id.isdecimal() or not (SITE / path.lstrip("/") / "index.html").exists():
            missing.append(f"Invalid shortlink {post_id}: {path}")
    if missing:
        raise SystemExit("\n".join(missing))
    print(f"OK: {len(pages)} HTML pages, {len(posts)} ship pages, {len(postmap)} shortlinks, {checked} local references")


if __name__ == "__main__":
    main()
