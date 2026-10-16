"""Build ShipWatcher's static prototype from data/ships.json."""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
if sys.argv[1:] not in ([], ["--site"]):
    raise SystemExit("Usage: python build.py [--site]")
OUTPUT = ROOT / ("site" if "--site" in sys.argv[1:] else "dist")
SHIPS = json.loads((ROOT / "data" / "ships.json").read_text(encoding="utf-8"))
ALL_LINES = ("Princess Cruises", "P&O Australia", "Cunard Line")
ACTIVE_SHIPS = [ship for ship in SHIPS if ship.get("active", True)]
LINES = tuple(line for line in ALL_LINES if any(ship["line"] == line for ship in ACTIVE_SHIPS))
QUOTES = json.loads((ROOT / "data" / "quotes.json").read_text(encoding="utf-8"))
COMENTARIO_DOMAIN_ID = "52efca07-e8eb-4711-8e66-83acaa93a8dd"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def validate() -> None:
    slugs: set[str] = set()
    post_ids: set[int] = set()
    for ship in SHIPS:
        slug = ship["slug"]
        post_id = ship["legacy_post_id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs or slug in {"about", "contact"}:
            raise ValueError(f"Invalid or duplicate slug: {slug}")
        if post_id is not None and (not isinstance(post_id, int) or post_id in post_ids):
            raise ValueError(f"Invalid or duplicate legacy post ID for {slug}")
        if ship["line"] not in ALL_LINES or not ship["name"].strip():
            raise ValueError(f"Missing name or unexpected cruise line for {slug}")
        url = urlsplit(ship["camera_url"])
        if url.scheme != "https" or not url.hostname:
            raise ValueError(f"Camera URL must use HTTPS for {slug}")
        slugs.add(slug)
        if not ship.get("active", True) and not ship.get("current_name"):
            raise ValueError(f"Historical ship needs a current name: {slug}")
        if post_id is not None:
            post_ids.add(post_id)
    if not QUOTES:
        raise ValueError("At least one homepage quote is required")
    for quote in QUOTES:
        if not all(quote.get(field) for field in ("text", "author", "work", "source")) or urlsplit(quote["source"]).scheme != "https":
            raise ValueError("Quotes need text, attribution and an HTTPS source")


def layout(title: str, description: str, main: str, *, page: str = "", comments_page_id: str = "", indexable: bool = True) -> str:
    comments_script = '<script defer src="https://comments.neilennis.com/comentario.js"></script>' if comments_page_id else ''
    comments = f'''<section class="comments-panel" aria-label="Comments"><h2>Comments</h2><comentario-comments theme="light" domain-id="{COMENTARIO_DOMAIN_ID}" page-id="{esc(comments_page_id)}"></comentario-comments></section>''' if comments_page_id else ''
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#082e43">
  <meta name="description" content="{esc(description)}">
  {'' if indexable else '<meta name="robots" content="noindex,follow">'}
  <title>{esc(title)} · ShipWatcher</title>
  <link rel="stylesheet" href="/assets/style.css">
  <script src="/assets/site.js" defer></script>
  {comments_script}
</head>
<body class="{'home' if page == 'home' else 'detail'}">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="/" aria-label="ShipWatcher home">
        <span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 42 42"><path d="M5 28h32l-5 7H11Z"/><path d="M10 26h22M14 22h16M18 18h9M22 8v10M4 39c6-3 10-3 16 0 6 3 10 3 18-1"/></svg></span>
        <span>Ship<span>Watcher</span></span>
      </a>
      <nav class="site-nav" aria-label="Main navigation">
        <a href="/" {'aria-current="page"' if page == 'home' else ''}>The fleet</a>
        <a href="/about/" {'aria-current="page"' if page == 'about' else ''}>About</a>
        <a href="/contact/" {'aria-current="page"' if page == 'contact' else ''}>Contact</a>
      </nav>
    </div>
  </header>
  <main id="main">{main}{comments}</main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div><strong>ShipWatcher</strong><p>An independent window onto the world's passenger ships.</p></div>
      <div class="footer-links"><a href="/about/">About</a><a href="/contact/">Contact</a><p>Camera images are supplied by their operators and may be unavailable.</p></div>
    </div>
  </footer>
</body>
</html>
"""


def camera_frame(ship: dict, *, detail: bool = False) -> str:
    name = esc(ship["name"])
    return f"""<div class="camera-visual{' camera-visual-large' if detail else ''}" data-camera-frame>
      <div class="camera-fallback" aria-hidden="true">
        <span class="fallback-horizon"></span>
        <svg viewBox="0 0 90 60" class="fallback-ship"><path d="M8 36h74l-8 12H18Z M18 32h54 M27 25h39 M35 18h23 M44 9v9 M3 54c12-5 18-5 29 0s18 5 29 0 18-5 26 0"/></svg>
        <span class="fallback-caption">Camera image unavailable</span>
      </div>
      <img src="{esc(ship['camera_url'])}" alt="Webcam image for {name}" loading="{'eager' if detail else 'lazy'}" referrerpolicy="strict-origin-when-cross-origin" data-camera-image>
      <span class="visual-corner" aria-hidden="true">↗</span>
    </div>"""


def card(ship: dict) -> str:
    return f"""<article class="ship-card" data-ship-card data-line="{esc(ship['line'])}" data-name="{esc(ship['name'].lower())}">
      <a href="/{esc(ship['slug'])}/" aria-label="View {esc(ship['name'])}">
        {camera_frame(ship)}
        <div class="card-body"><span class="eyebrow">{esc(ship['line'])}</span>
          <div class="card-title-row"><h3>{esc(ship['name'])}</h3><span class="card-arrow" aria-hidden="true">↗</span></div>
          <span class="card-caption">View ship camera</span>
        </div>
      </a>
    </article>"""


def home_page() -> str:
    cards = "\n".join(card(ship) for ship in sorted(ACTIVE_SHIPS, key=lambda s: (LINES.index(s["line"]), s["name"])))
    chips = '\n'.join(f'<button type="button" class="filter-chip" data-filter="{esc(line)}" aria-pressed="false">{esc(line)}</button>' for line in LINES)
    first = QUOTES[0]
    quote_data = json.dumps(QUOTES, ensure_ascii=False).replace("<", "\\u003c")
    main = f"""
    <section class="hero">
      <div class="wrap hero-grid">
        <div class="hero-copy">
          <span class="section-label"><span class="label-line"></span> The view from the bridge</span>
          <h1 data-hero-quote>“{esc(first['text'])}”</h1>
          <p class="quote-credit">— <span data-quote-author>{esc(first['author'])}</span>, <a data-quote-source href="{esc(first['source'])}" target="_blank" rel="noopener noreferrer"><cite data-quote-work>{esc(first['work'])}</cite> ↗</a></p>
          <script type="application/json" id="homepage-quotes">{quote_data}</script>
          <p>Follow the view from passenger ships around the world. Choose a ship, open its camera, and see where the horizon takes you.</p>
          <a class="hero-link" href="#fleet">Explore the cameras <span aria-hidden="true">↗</span></a>
          <div class="hero-facts"><div><strong>{len(ACTIVE_SHIPS):02d}</strong><span>Ships in the catalog</span></div><div><strong>{len(LINES):02d}</strong><span>Cruise lines</span></div></div>
        </div>
        <div class="hero-art">
          <img src="/assets/hero.svg" alt="Illustration of a cruise ship crossing blue water" width="800" height="560">
          <span class="art-note">An open horizon, one ship at a time</span>
        </div>
      </div>
    </section>
    <section id="fleet" class="fleet-section wrap" aria-labelledby="fleet-title">
      <div class="section-heading"><div><span class="section-label dark"><span class="label-line"></span> Browse the fleet</span><h2 id="fleet-title">Ship cameras</h2></div><p>Browse by cruise line or find a ship by name.</p></div>
      <div class="fleet-tools"><div class="filters" role="group" aria-label="Filter by cruise line"><button type="button" class="filter-chip active" data-filter="all" aria-pressed="true">All ships</button>{chips}</div>
        <label class="search-field"><span class="visually-hidden">Search ships</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg><input type="search" placeholder="Find a ship" autocomplete="off" data-ship-search></label></div>
      <div class="results-heading"><p id="results-count" role="status">Showing all {len(ACTIVE_SHIPS)} ships</p><span>Camera images from cruise operators</span></div>
      <div class="ship-grid" id="ship-grid">{cards}</div>
      <p class="empty-state" data-empty hidden>No ships match that search. Try a different name or cruise line.</p>
    </section>
    <section id="about" class="about-section"><div class="wrap about-grid"><div><span class="section-label dark"><span class="label-line"></span> About this collection</span><h2>A front-row seat<br>to the open water.</h2></div><div><p>ShipWatcher brings together links to passenger-ship webcam images in one place. The cameras are run by cruise lines, so their images and availability can change without notice.</p><p>This is an independent catalog. A loaded camera image may be a still frame and does not guarantee a live feed.</p></div></div></section>
    """
    return layout("Ship cameras", "Explore passenger ship webcam images by cruise line and ship name.", main, page="home")


def about_page() -> str:
    main = """
    <div class="wrap editorial-page">
      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">All cameras</a><span aria-hidden="true">/</span><span>About</span></nav>
      <div class="editorial-grid"><div><span class="section-label dark"><span class="label-line"></span> The story behind ShipWatcher</span><h1>For the love<br>of ships.</h1><p class="editorial-intro">A few minutes at a ship's bridge can take you a long way.</p></div>
      <div class="editorial-copy"><p>Ships have been part of my life since my earliest memory. In 1965, my family migrated from the UK to Australia aboard <em>Ellinis</em>. My father had made a sea journey of his own as a child, travelling from India to Scotland aboard <em>Tegelberg</em> in the late 1940s. The family trail reaches back to 1841, when Thomas Ennis sailed from England to Madras aboard <em>Columbus</em>.</p>
      <p>Perhaps that is why I still find myself drawn to a ship on the horizon. I made ShipWatcher for anyone who shares that curiosity. It gathers passenger-ship cameras in one place, so you can follow a vessel across the water or take a short virtual cruise from your desk.</p>
      <p>The camera images belong to the cruise operators. Some are still frames, and their availability changes. I keep this independent catalog as a place to enjoy the view and discover where each ship may be travelling.</p>
      <p class="editorial-signoff">— Neil Ennis</p>
      <a class="editorial-action" href="/">Explore the fleet <span aria-hidden="true">↗</span></a></div></div>
    </div>"""
    return layout("About", "The family story and love of ships behind ShipWatcher.", main, page="about")


def contact_page() -> str:
    main = """
    <div class="wrap editorial-page">
      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">All cameras</a><span aria-hidden="true">/</span><span>Contact</span></nav>
      <div class="editorial-grid"><div><span class="section-label dark"><span class="label-line"></span> Get in touch</span><h1>Send a note<br>ashore.</h1><p class="editorial-intro">Found a new camera, or a link that needs updating? I'd love to hear from you.</p></div>
      <div class="editorial-copy"><p>Use my existing contact form to send a message about ShipWatcher. Mention the ship name or page address if you're reporting a camera problem.</p>
      <a class="editorial-action" href="https://blog.neilennis.com/contact/" target="_blank" rel="noopener noreferrer">Open Neil's contact form <span aria-hidden="true">↗</span></a>
      <p class="contact-note">The form opens on my personal blog. Your message is sent there; this static site does not collect it.</p></div></div>
    </div>"""
    return layout("Contact", "Contact Neil Ennis about ShipWatcher and its ship cameras.", main, page="contact")


def ship_page(ship: dict, index: int) -> str:
    next_ship = ACTIVE_SHIPS[(index + 1) % len(ACTIVE_SHIPS)]
    main = f"""
    <div class="wrap ship-detail">
      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">All cameras</a><span aria-hidden="true">/</span><span>{esc(ship['name'])}</span></nav>
      <div class="detail-heading"><div><span class="section-label dark"><span class="label-line"></span> {esc(ship['line'])}</span><h1>{esc(ship['name'])}</h1><p>A ship's-eye view from an external camera.</p></div><a class="back-link" href="/">← Back to the fleet</a></div>
      <div class="detail-grid"><section class="camera-panel" aria-label="{esc(ship['name'])} camera">
        {camera_frame(ship, detail=True)}
        <div class="camera-controls"><div><span class="panel-kicker">Camera image</span><p>Provided by {esc(ship['line'])}. Availability can change.</p></div><div class="control-actions"><button type="button" class="text-button" data-camera-refresh>↻ Refresh image</button><a class="text-button" href="{esc(ship['camera_url'])}" target="_blank" rel="noopener noreferrer">Open source image ↗</a></div></div>
      </section><aside class="detail-aside"><span class="aside-number">{index + 1:02d} / {len(ACTIVE_SHIPS):02d}</span><h2>Watching the<br>waterline.</h2><p>Webcam images are hosted by the ship operator. A loaded camera image may be a still frame and availability can change.</p><div class="aside-rule"></div><span class="eyebrow">Up next</span><a class="next-ship" href="/{esc(next_ship['slug'])}/">{esc(next_ship['name'])} <span aria-hidden="true">↗</span></a></aside></div>
      {f'<p class="identity-note">{esc(ship["identity_note"])}</p>' if ship.get('identity_note') else ''}
    </div>"""
    return layout(ship["name"], f"View the {ship['name']} webcam image in the ShipWatcher catalog.", main, comments_page_id=f"/{ship['slug']}/")


def historical_page(ship: dict) -> str:
    main = f"""
    <div class="wrap editorial-page">
      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">All cameras</a><span aria-hidden="true">/</span><span>{esc(ship['name'])}</span></nav>
      <div class="editorial-grid"><div><span class="section-label dark"><span class="label-line"></span> Former camera listing</span><h1>{esc(ship['name'])}</h1><p class="editorial-intro">This ship has continued its journey under another name.</p></div>
      <div class="editorial-copy"><p>The former {esc(ship['name'])} is now known as <strong>{esc(ship['current_name'])}</strong>. The old {esc(ship['line'])} camera is no longer included in the active ShipWatcher catalog.</p>
      <p>This page remains available so older links still make sense. It does not imply the vessel was scrapped.</p>
      <a class="editorial-action" href="/">See current cameras <span aria-hidden="true">↗</span></a></div></div>
    </div>"""
    return layout(ship["name"], f"Historical listing for the former {ship['name']} camera.", main, comments_page_id=f"/{ship['slug']}/", indexable=False)


def main() -> None:
    validate()
    def write_page(path: Path, markup: str) -> None:
        path.write_text("\n".join(line.rstrip() for line in markup.splitlines()) + "\n", encoding="utf-8")

    # Only the generated directory inside this project is replaced.
    if OUTPUT.resolve().parent != ROOT or OUTPUT.is_symlink():
        raise RuntimeError("Unexpected output directory")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / "assets").mkdir(parents=True)
    write_page(OUTPUT / "index.html", home_page())
    for slug, page in (("about", about_page()), ("contact", contact_page())):
        folder = OUTPUT / slug
        folder.mkdir()
        write_page(folder / "index.html", page)
    for ship in SHIPS:
        folder = OUTPUT / ship["slug"]
        folder.mkdir()
        page = ship_page(ship, ACTIVE_SHIPS.index(ship)) if ship in ACTIVE_SHIPS else historical_page(ship)
        write_page(folder / "index.html", page)
    for asset in ("hero.svg", "style.css", "site.js"):
        shutil.copy2(ROOT / "assets" / asset, OUTPUT / "assets" / asset)
    (OUTPUT / "ships.json").write_text(json.dumps(SHIPS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    postmap = {str(s["legacy_post_id"]): f"/{s['slug']}/" for s in SHIPS if s["legacy_post_id"] is not None}
    (OUTPUT / "postmap.json").write_text(json.dumps(postmap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    indexed_paths = ["/", "/about/", "/contact/", *(f"/{ship['slug']}/" for ship in ACTIVE_SHIPS)]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>https://shipwatcher.com{path}</loc></url>\n" for path in indexed_paths)
    sitemap += "</urlset>\n"
    (OUTPUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (OUTPUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://shipwatcher.com/sitemap.xml\n", encoding="utf-8")
    redirects = [
        "/feed/ /feed.xml 301", "/wp-sitemap.xml /sitemap.xml 301",
        "/author/neilennis/ / 301", "/author/neilennis/page/2/ / 301", "/author/neilennis/page/3/ / 301",
        "/category/cunard-line/ / 301", "/category/p-o-australia/ / 301", "/category/princess-cruises/ / 301",
        "/category/princess-cruises/page/2/ / 301", "/page/2/ / 301", "/page/3/ / 301",
    ]
    (OUTPUT / "_redirects").write_text("\n".join(redirects) + "\n", encoding="utf-8")
    write_page(OUTPUT / "404.html", layout("Page not found", "This ShipWatcher page could not be found.", '<div class="wrap editorial-page"><span class="section-label dark"><span class="label-line"></span> Lost at sea</span><h1 class="not-found-title">Page not found.</h1><p>That address is not in our logbook. The fleet is still close by.</p><a class="editorial-action" href="/">Return to the fleet <span aria-hidden="true">↗</span></a></div>', indexable=False))
    legacy_feed = ROOT / "legacy" / "feed.xml"
    if legacy_feed.exists():
        shutil.copy2(legacy_feed, OUTPUT / "feed.xml")
    print(f"Built index, {len(ACTIVE_SHIPS)} active and {len(SHIPS) - len(ACTIVE_SHIPS)} historical ship pages in {OUTPUT}")


if __name__ == "__main__":
    main()
