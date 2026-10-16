# ShipWatcher static site

This repository builds [ShipWatcher.com](https://shipwatcher.com/) from a small
ship catalog. It requires Python 3 to build and no WordPress installation,
database, framework, or package manager. The deployed site lives in `site/`.

## Update the catalog

Edit `data/ships.json` to add or update a ship. Use an operator's HTTPS webcam
URL when possible, and check that it identifies the right ship. Set `active`
to `false` for a retired listing: its old page remains available with a clear
historical notice, while the fleet page no longer shows it. `data/quotes.json`
contains the five approved, sourced homepage quotes. Keep the quote text and
attribution together.

Build and check the deployable site from this repository's root:

```powershell
python build.py --site
python check.py --site
python scripts/check_site.py
```

For a local preview, run `python build.py` and serve `dist/` with an HTTP
server. For example:

```powershell
python -m http.server 8987 --bind 127.0.0.1 --directory dist
```

The local server shows pages and assets but does not execute `worker.mjs`.
Check old `/?p=ID` shortlinks on the Cloudflare preview or live Worker.

## Published behavior

`build.py` creates the fleet page, About and Contact pages, 20 active ship
pages, six historical ship pages, the old 23-post shortlink map, sitemap,
robots file, redirects, and a custom 404 page. The imported RSS feed is kept
in `legacy/feed.xml` and copied to `site/feed.xml` at build time. It is a
historical feed, not a feed of new catalog changes.

Ship pages retain their original paths as Comentario page IDs. Preserve those
paths and the domain ID in `build.py` so existing discussions stay attached.
The original WordPress snapshot is available in Git history before the
catalog replacement; no PHP, database or private backup belongs here.

The webcam images come from third-party operators and can stop working. The
page shows an unavailable-camera message when an image fails. `CATALOG_REVIEW.md`
records dated findings and candidates for catalog updates.

## Deployment and rollback

Cloudflare builds the `shipwatcher-com` Worker automatically from the connected
GitHub production branch. `wrangler.jsonc` serves the generated `site/` assets.
`worker.mjs` keeps `www.shipwatcher.com` redirected to the apex address and
preserves old WordPress `/?p=ID` shortlinks. `site/_redirects` retains the
feed and sitemap aliases and points old listing archives to the fleet page.

To roll back this replacement, redeploy the earlier Git commit `8af770d`.
Both live hostnames were already connected to this Worker before the catalog
replacement; no DNS change is part of this release.

The previous WordPress export and its public assets were made from the public
site in October 2026. `scripts/export_public.py` documents that one-time
process; it is not part of normal catalog maintenance.
