# Lateral Repairs — Marketing Website

A fully animated marketing site for **Lateral Repairs** (UAB "Lateral repairs"),
an independent manufacturer of CIPP liners and supplier of no-dig trenchless pipe & sewer
rehabilitation solutions, based in Tauragė, Lithuania — now part of the European
trenchless platform founded around **IMS Trenchless & Polypipe** (April 2026).

This is a **separate product** from the Lateral Repairs mobile app (the resin calculator /
datasheet tool). The site links out to the app on the App Store and Google Play.

## Stack

Zero-build static site — pure HTML, CSS and vanilla JS, plus **Three.js** (CDN) for the
3D hero. No install step; deploys instantly to any static host (Vercel, Netlify,
GitHub Pages, S3…).

```
index.html              # all sections
assets/css/styles.css   # brand system + layout + animations
assets/js/main.js       # preloader, nav, scroll reveals, tilt cards, 3D hero
images/                 # logo, app-store badges, favicons
vercel.json             # caching + security headers
```

## Design system

- **Palette:** strictly pink / white / black — magenta `#e6007e` & `#ff4fb0`,
  near-black `#070608`, white/off-white surfaces. Dark and light sections alternate.
- **Type:** Space Grotesk (headings) + Inter (body).
- **Logo:** the official Lateral Repairs droplet mark (`images/logo.png`) is the primary
  brand element — preloader, nav, phone mockup, footer and favicons all use it.

## Animation

- **3D hero (Three.js):** the camera drifts through a tunnel of pink particle rings —
  the inside of a freshly relined pipe — with a wireframe shell, floating dust,
  fog and mouse parallax. Renders only while on screen; falls back to a CSS gradient
  when WebGL or the CDN is unavailable.
- **3D tilt cards** with cursor-follow glow (products, partners, stats, certifications)
  and a 3D-swaying phone mockup.
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
| Polypipe | CIPP liner systems | [polypipe.de](https://polypipe.de/en) |
| Amex Sanivar | Pressure pipe liners & repair seals | [amex-sanivar.com](https://www.amex-sanivar.com/) |
| Resinnovation | High-performance synthetic resins | [resinnovation.com](https://www.resinnovation.com/en/) |
| Kardiam | Diamond milling & cutting tools | [kardiam.eu](https://www.kardiam.eu/?lang=en) |
| Hurricane Trenchless | Liner curing systems & vehicle fit-outs | [hurricane-tt.de](https://hurricane-tt.de/en/) |

## Content sources

- Company facts, products, certifications and the company video are reused from the
  Lateral Repairs app and the official site (lateralrepairs.com).
- All photography is self-hosted in `images/` — real product liners, job-site and equipment shots supplied by the company.
- Group/partner facts from the public announcement (Trenchless Works, Apheon,
  ims-robotics.de, resinnovation.com).
- Legal data: UAB "Lateral repairs" · company code 304403126 · VAT LT100010469717 ·
  Paberžių g. 5, LT-72328 Tauragė, Lithuania.

## ⚠️ Before launch — TODO

1. **Contact form** — currently a front-end prototype (no backend). Wire it to email/CRM
   (e.g. Vercel serverless function, Formspree, or your inbox) before going live.
2. **App Store / Play links** — verified live, but confirm the listings are the correct
   public ones for your region.
3. **Custom domain** — add it in your Vercel project settings once deployed.

## Local preview

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Deploy (keep it separate from the app)

Import this repo/branch as a **new** Vercel project (e.g. `lateral-repairs-web`) so it does
not overwrite the existing app project. Framework preset: **Other** (static). No build command.
