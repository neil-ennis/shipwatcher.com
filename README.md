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

## Migration notes

The snapshot was made on 16 October 2026 from the public website. The live
domain can be connected only after reviewing the Cloudflare preview and
confirming that Comentario is configured. Record the previous DNS targets
before changing them, and leave the AWS site available for rollback until the
new live site has been checked.
