# Ship catalog review — 16 October 2026

## Update — 8 November 2026

Added [Explora I](https://explorajourneys.panomax.com/explora-1),
[Viking Sea](https://viking.panomax.com/sea), and
[MS EUROPA](https://hlkf.panomax.com/ms-europa) from the
[Panomax live-camera directory](https://cruises.panomax.com/live-cameras).
Their operator pages and direct `preview_og.jpg` images returned HTTP 200 on
8 November 2026; the image responses were JPEGs. Added Hapag-Lloyd Cruises as
its own fleet filter. These are provider-hosted cameras, so the image fallback
still applies if a feed becomes unavailable.

## Update — 31 October 2026

Added Viking Vesta, Viking Mira and Explora III to the local catalog. Each has
an updating [Panomax](https://cruises.panomax.com/live-cameras) JPEG preview
and a separate link to its live interactive panorama. The three preview JPEGs
and panorama pages returned HTTP 200 on 31 October. These are provider-hosted
images, so continued availability and permission to embed remain external
dependencies. The fleet filters now include Viking and Explora Journeys.

No P&O camera was added. The [P&O Cruises camera directory](https://www.cruisingearth.com/ship-webcams/po-cruises/)
says its public onboard cameras are decommissioned. P&O UK still describes a
ship webcam on [in-cabin televisions](https://www.pocruises.com/help-hub/centre/life-on-board/cabins/cabin-facilities-and-amenities),
which does not establish a public feed. P&O Australia was absorbed by
[Carnival in March 2025](https://www.carnival.com.au/carnival-and-pocruises).
The old Pacific ship pages stay historical until a current public camera is
verified.

The 23 imported entries remain in the prototype. Six obsolete camera listings
are hidden from the active fleet but retain historical pages and original
shortlinks. A retired ship *name* does not mean the physical vessel has been
scrapped. Three new Princess records bring the catalog to 20 active views.

## Entries whose listed operator/name has ended

| Catalog entry | Evidence | Proposed treatment |
| --- | --- | --- |
| Pacific Aria | P&O Australia no longer operates it; the vessel now sails as Celestyal Journey. [Current operator](https://celestyal.com/us/our-ships/celestyal-journey), [vessel history](https://www.marhisdata.nl/public/publicaties/publicatie_2023-03-12_db19397c609f70e80a4c4a64b8c45cc3.pdf) | Remove old camera entry or replace with an operator-supported Celestyal camera if one exists. |
| Pacific Dawn | The former vessel sails as Ambience. [Current operator](https://www.ambassadorcruiseline.com/our-ships/ambience/profile/), [history](https://cruiseindustrynews.com/cruise-news/2026/09/ambassadors-ambience-celebrates-35-years/) | Remove old P&O camera entry; retain a historical redirect if deployed. |
| Pacific Explorer | Carnival sold it and it left P&O Australia in 2025. [Carnival fleet disclosure](https://www.carnivalcorp.com/wp-content/uploads/2024/10/Ships-in-our-Fleet-as-of-August-31-2024.pdf), [later name/report](https://cruiseindustrynews.com/cruise-news/2025/01/updated-list-heres-what-happening-with-the-po-australia-fleet/) | Remove old P&O camera entry, subject to direct source check. |
| Golden Princess | Princess transferred it to P&O as Pacific Adventure; it now sails as Carnival Adventure. [Princess announcement](https://es-www.princess.com/en-au/news/news-releases/2020/10/princess-cruises-advances-transition-of-golden-princess-and-star-princess-to-sister-company-po-cruises-australia), [Carnival history](https://www.carnival.com.au/behind-the-seas/life-onboard/carnival-adventure-features/) | Remove its old Princess camera listing. |
| Pacific Princess | Princess sold the vessel in 2021; it now sails as Azamara Onward. [Princess notice](https://www.princess.com/content/dam/princess/cruise-planning/pdfs/impacted-cancelled-cruises/cancellation-pacific-princess-cruises.pdf.coredownload.inline.pdf), [Azamara](https://www.azamara.com/ca/our-ships/azamara-onward) | Remove its old Princess camera listing. |
| Sea Princess | Princess sold it in 2020; a later owner operates it as Dream. [Princess notice](https://www.princess.com/en-int/news/news-releases/2020/09/sun-princess-and-sea-princess-to-leave-princess-cruises-fleet), [later service](https://cruiseindustrynews.com/cruise-news/2023/07/former-sea-princess-completes-refit-at-shipyard-in-china/) | Remove its old Princess camera listing. |

**Name reuse needs care:** The catalog's Star Princess and Sun Princess records
originated before Princess sold those older vessels. Princess now operates
*new* ships with the same two names and lists both on its [current bridgecam
page](https://www.princess.com/ships-and-experience/ships/bridgecams). These
records should be explicitly updated to identify the new vessels and confirm
their camera image URLs; they should not simply be deleted by name. The old
Star Princess became Pacific Encounter and then Carnival Encounter. Princess
documents the first transfer in its [2020 announcement](https://es-www.princess.com/en-au/news/news-releases/2020/10/princess-cruises-advances-transition-of-golden-princess-and-star-princess-to-sister-company-po-cruises-australia).

No catalog vessel was confirmed physically destroyed in this review.

## New webcam candidates

Princess's [current official bridgecam page](https://www.princess.com/ships-and-experience/ships/bridgecams)
lists three ships missing from the imported catalog. On 16 October 2026, the
page's Discovery, Enchanted and Regal camera images loaded in the browser and
their image addresses were confirmed before adding them locally:

- Discovery Princess
- Enchanted Princess
- Regal Princess

Queen Anne was not proposed: a current operator-hosted webcam was not verified.

No Carnival Cruise Line onboard webcam was added. Carnival's current [fleet
pages](https://www.carnival.com.au/behind-the-seas/life-onboard/carnival-adventure-carnival-encounter/)
confirm ships such as Adventure and Encounter but provide no public bridge
camera. An independent [camera directory](https://www.cruisingearth.com/ship-webcams/carnival-cruise-line/carnival-sunrise/)
marks an older Carnival camera decommissioned. A [shipyard webcam](https://www.meyerwerft.de/en/company/webcam)
shows construction of Carnival Festivale, but that is not an onboard camera.

## Deployment boundary

The six old entries are presented as historical ships with no active camera.
Old page paths and `postmap.json` mappings are preserved. This is only in the
local proof of concept; the live site and repository are unchanged.
