# Lateral Repairs — Marketing Website

A fully animated marketing site for **Lateral Repairs** (UAB "Lateral repairs"),
a manufacturer of CIPP liners and supplier of no-dig trenchless pipe & sewer
rehabilitation solutions, based in Tauragė, Lithuania — now part of the European
trenchless platform founded around **IMS Trenchless & Polypipe** (April 2026).

This is a **separate product** from the Lateral Repairs mobile app (the resin calculator /
datasheet tool). The site links out to the app on the App Store and Google Play.

> The app itself (React 19 + Vite) lives in [`app/`](./app) — restored from the
> original source. Deploy it as its own project; see [`app/README.md`](./app/README.md).

## Stack

Zero-build static site — pure HTML, CSS and vanilla JS, plus a self-hosted **Three.js**
build for the 3D hero. No install step. Production target: Apache hosting at
Serveriai.lt (`https://www.lateralrepairs.com/`), alongside the existing CMS Made Simple site.

```
index.html              # all sections
products/*.html         # generated product pages — do not hand-edit
tools/build-products.py # product catalogue: pages, mega-menu, drawer, browser
lr-assets/css/styles.css   # brand system + layout + animations
lr-assets/js/main.js       # preloader, nav, drawer, catalogue, reveals, 3D hero
lr-assets/datasheets/      # technical + safety data sheets (PDF)
lr-assets/images/          # logo, wordmark, photography, favicons
# all frontend assets live in lr-assets/ — CMS Made Simple already owns a top-level assets/
tools/build-deploy.py   # builds deployment/public_html (the exact upload) + MANIFEST
tools/merge_htaccess.py # adds the 2 frontend blocks to a LOCAL copy of the production .htaccess
tools/qa/               # static + browser QA (run-all.sh); apache_check.py = .htaccess before/after test
deployment/             # upload package, DEPLOY.md (release runbook), .htaccess additions
vercel.json             # preview deployments only — never uploaded to production
```

Run `python3 tools/build-products.py` after editing the catalogue. It regenerates
every product page and re-injects the mega-menu, the mobile drawer and the home-page
catalogue browser from one source.

## Design system

- **Palette:** strictly pink / white / black — magenta `#e6007e` & `#ff4fb0`,
  near-black `#070608`, white/off-white surfaces. Dark and light sections alternate.
- **Type:** Space Grotesk (headings) + Inter (body).
- **Logo:** the official Lateral Repairs droplet mark, converted from the supplied vector
  artwork to `lr-assets/images/logo.svg` (2.5 KB, transparent, sharp at any size). Used by the
  preloader, nav, hero, phone mockup and footer; PNG icons remain for favicons.

## Animation

- **3D hero (Three.js):** the camera drifts through a tunnel of pink particle rings —
  the inside of a freshly relined pipe — with a wireframe shell, floating dust,
  fog and mouse parallax. Renders only while on screen; falls back to a CSS gradient
  when WebGL is unavailable.
- **3D tilt cards** with cursor-follow glow (products, partners, stats, certifications)
  and a 3D-swaying phone mockup.
- **Hero logo dock:** the brand mark opens large in the hero and eases up into its nav
  slot as you scroll (transform-only, so it lands pixel-perfect); scrolling back up
  returns it. The wordmark fades in on docking.
- **Scroll choreography:** preloader with floating droplet, scroll-progress bar,
  staggered reveals, count-up stats, scroll-spy nav, infinite marquee,
  hero headline line-rise.
- Honors `prefers-reduced-motion` (animations and the 3D canvas are disabled).

## IMS Group section

On 30 April 2026 Lateral Repairs joined the newly founded group around IMS Trenchless
and Polypipe — a European platform in trenchless pipe rehabilitation backed by financial
partner [Apheon](https://www.apheon.com/). MD Drew Holland joined the group's shareholding.
The `#group` section links to all partner companies:

| Company | Speciality | Link |
| --- | --- | --- |
| IMS Robotics | Sewer rehabilitation robots & milling systems | [ims-robotics.de](https://www.ims-robotics.de/en/home) |
| Polypipe | Coating systems for trenchless in-house pipe rehabilitation | [polypipe.de](https://polypipe.de/en) |
| Amex Sanivar | Pressure pipe liners & repair seals | [amex-sanivar.com](https://www.amex-sanivar.com/) |
| resinnovation | High-performance synthetic resins | [resinnovation.com](https://www.resinnovation.com/en/) |
| Kardiam | Diamond milling & cutting tools | [kardiam.eu](https://www.kardiam.eu/?lang=en) |
| Hurricane Trenchless | Liner curing systems & vehicle fit-outs | [hurricane-tt.de](https://hurricane-tt.de/en/) |

## Content sources

- Company facts, products, certifications and the company video are reused from the
  Lateral Repairs app and the official site (lateralrepairs.com).
- All photography is self-hosted in `lr-assets/images/` — real product liners, job-site and equipment shots supplied by the company.
- Group/partner facts from the public announcement (Trenchless Works, Apheon,
  ims-robotics.de, resinnovation.com).
- Legal data: UAB "Lateral repairs" · company code 304403126 · VAT LT100010469717 ·
  Paberžių g. 5, LT-72328 Tauragė, Lithuania.

## Before launch

See **[deployment/DEPLOY.md](deployment/DEPLOY.md)** — deployment gates, upload list,
`.htaccess` additions, backup, rollback and post-deployment tests. In short:

1. **Contact form — NOT CONNECTED.** No backend exists in this repository; the form says so
   to visitors and never claims success. It needs the production PHP handler (DEPLOY.md §11).
2. **Privacy policy** — resolve the highlighted `[TO CONFIRM …]` markers in `privacy.html`.

## Build & QA

```bash
python3 tools/build-products.py   # pages, menus, consent banner, sitemap
python3 tools/build-deploy.py     # deployment/public_html + MANIFEST.sha256
sh tools/qa/run-all.sh            # determinism, JS syntax, package, static + browser QA
```

Browser QA needs `pip install playwright` and a Chromium that Playwright can launch.

## Local preview

```bash
python3 -m http.server 8000 --directory deployment/public_html   # http://localhost:8000
```

## Vercel preview (not production)

The Vercel project only serves review previews. `vercel.json` mirrors production behaviour
(real `.html` URLs, same headers); `.vercelignore` keeps `deployment/` and `tools/` off previews.
