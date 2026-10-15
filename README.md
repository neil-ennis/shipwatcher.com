# ShipWatcher.com static site

This repository contains a public-only snapshot of the original ShipWatcher.com
WordPress site, prepared for Cloudflare Workers Static Assets. The old local
WordPress installation was not used for this export because it contained
malicious PHP. No PHP, database, private backups, or WordPress administration
files belong in this repository.

## Contents

- `site/` is the deployable site: 23 ship pages, archives, theme assets, a
  sitemap, RSS feed, and the map of old WordPress post IDs.
- `worker.mjs` preserves old `/?p=123` shortlinks using `site/postmap.json`.
  It also redirects `www.shipwatcher.com` to the apex domain, preserving the
  path and query string.
- `site/shipwatcher.css` fits webcam images within the viewport and styles the
  comment area and unavailable-webcam message.
- `site/shipwatcher.js` shows that message when an external webcam image fails.
- `scripts/export_public.py` records how this snapshot was made from publicly
  available pages; it is not a routine build step.

The original footer's placeholder links were removed. WordPress comment forms
were replaced by Comentario with a stable page ID matching each ship's path.
Comentario uses the existing `shipwatcher.com` registration and its domain ID
on each ship page. The page IDs preserve the paths of all 23 existing comment
threads. The preview host must be added to that domain's allowed origins before
comments can render there; preserve `$` for the live domain.

## Deploy and maintain

Cloudflare builds this Worker from the GitHub repository. A commit to the
connected production branch should trigger a new deployment. `wrangler.jsonc`
sets `site/` as the assets directory. The Worker is required for query-string
shortlinks, so do not deploy the `site/` directory as a standalone Pages site.

To check a proposed change locally, serve `site/` using an HTTP server and run
`python scripts/check_site.py`. A plain local server will serve pages and
assets but will not execute `worker.mjs`; test old `/?p=` links on the Cloudflare
preview before changing DNS.

The webcam images remain on cruise-line servers. Their availability is outside
this repository's control. The message on a failed image preserves the page
and its link; replace an image URL only after verifying a reliable new source
and the right to use it.

## Future design

The current WordPress-derived layout is functional but visually sparse.
Redesign it to make the ship webcams the focus again. Neil identified the
[17 June 2016 Wayback capture](https://web.archive.org/web/20160617005811/http://shipwatcher.com/)
as the visual reference. It shows a grid of live webcam images near the top,
a blue masthead, location details beneath the cameras, ship selection
controls, and a compact news sidebar. Adapt those strengths to a modern,
responsive layout; do not assume the old live feeds and controls still work.
Preserve ship page URLs, old post shortlinks, Comentario threads, and clear
fallbacks for unavailable external webcams. Review a design preview with Neil
before publishing it.

## Migration notes

The snapshot was made on 16 October 2026 from the public website. Both
`shipwatcher.com` and `www.shipwatcher.com` are connected to the production
Cloudflare Worker. The previous DNS records were CNAMEs to
`d1pvxa10u1hkdi.cloudfront.net`, DNS only, TTL Auto. The apex record had
the comment `flattened from ANAME which is not available in Cloudflare`.
Keep the old AWS site available for rollback until the live site is accepted.

`wrangler.jsonc` uses `run_worker_first: true`: the Worker must receive
every path so `www` redirects even when a matching static asset exists.
The Comentario allowed origins are the live domain (`$`) and
`shipwatcher-com.aged-night-bf73.workers.dev` for preview comments.
