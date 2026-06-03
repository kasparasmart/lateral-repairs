# Lateral Repairs — Marketing Website

A professional, release-ready marketing site for **Lateral Repairs** (UAB "Lateral repairs"),
an independent manufacturer of CIPP liners and supplier of no-dig trenchless pipe & sewer
rehabilitation solutions, based in Tauragė, Lithuania.

This is a **separate product** from the Lateral Repairs mobile app (the resin calculator /
datasheet tool). The site links out to the app on the App Store and Google Play.

## Stack

Zero-build static site — pure HTML, CSS and vanilla JS. No dependencies, no install step,
deploys instantly to any static host (Vercel, Netlify, GitHub Pages, S3…).

```
index.html              # all sections
assets/css/styles.css   # brand system + layout + animations
assets/js/main.js        # nav, scroll reveals, count-up, parallax, lazy video
images/                  # logo, app-store badges, favicon (SVG)
vercel.json              # caching + security headers
```

## Brand

Palette is taken directly from the Lateral Repairs app:
near-black `#0a0a0a`, neon pink `#e91e8c` / `#9b1260`, cyan `#00bcd4`.
Headings in Space Grotesk, body in Inter.

## Content sources

- Company facts, products, certifications and the company video are reused from the
  Lateral Repairs app and the official site (lateralrepairs.com).
- The 6 facility / product photos are served from the company's own CDN
  (`www.lateralrepairs.com/uploads/...`).
- Legal data: UAB "Lateral repairs" · company code 304403126 · VAT LT100010469717 ·
  Paberžių g. 5, LT-72328 Tauragė, Lithuania.

### Logo

`images/logo.png` is the **official Lateral Repairs droplet mark**, processed from the
supplied artwork: the white background was knocked out to transparency (the white "LR"
letters are preserved) so it sits cleanly on the dark theme. App icons / favicons
(`icon-192`, `icon-512`, `apple-touch-icon`) are generated from the same mark. The nav and
footer pair the mark with a CSS wordmark lockup.

## ⚠️ Before launch — TODO

1. **Contact form** — currently a front-end prototype (no backend). Wire it to email/CRM
   (e.g. Vercel serverless function, Formspree, or your inbox) before going live.
3. **App Store / Play links** — verified live, but confirm the listings are the correct
   public ones for your region.
4. **Custom domain** — add it in your Vercel project settings once deployed.

## Local preview

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Deploy (keep it separate from the app)

Import this repo/branch as a **new** Vercel project (e.g. `lateral-repairs-web`) so it does
not overwrite the existing app project. Framework preset: **Other** (static). No build command.
