# Lateral Repairs — App

The installer-facing mobile app, restored from the original source. React 19 +
Vite. Single-file UI in `src/App.jsx` (inline styles, no CSS framework), with
seven screens: **Home, Mix Calc, Cure Timer, Tech Data, Certificates, Media,
Contact**. This is a **separate product** from the marketing website in the repo
root.

## Run locally

```bash
cd app
npm install
npm run dev      # http://localhost:5173
npm run build    # outputs to app/dist
npm run lint
```

## Images

The app loads brand photos from `public/images/` (referenced in `App.jsx` → `IMG`).
These were rasterized from the supplied print PDFs (1500 px, ~q82):

| File | Source PDF | Used on |
|------|------------|---------|
| `logo.jpg` | Grafik_Logo (transparent PNG) | header |
| `top-wall.jpg` | Top_wall 400×170 | Home hero |
| `backwall-desni.jpg` | Backwall Desni 160×280 | Home footer band |
| `backwall-levi.jpg` | Backwall Levi 160×280 | Cure Timer |
| `backwall-425.jpg` | Backwall 425×280 | Contact |
| `backwall-400.jpg` | *(reused from `backwall-425`)* | Calculator / Certificates |
| `banner.jpg` | Banner 80×240 | (defined, currently unused) |

`backwall-400.jpg` has no dedicated artwork yet — it's a copy of `backwall-425.jpg`.
Drop a real `backwall-400.jpg` in to replace it.

## The resin formula (sales-grade, datasheet-driven)

Resin quantity comes from the **official kg/m tables printed in the MULTIline
datasheets** (V2026.1, the PDFs in Tech Data), interpolated by DN, times length,
plus a selectable wet-out margin (default +10 %). The A/B split uses each resin
system's own mix ratio (epoxies 100:30 by weight with densities A 1.153 /
B 1.079 kg/L — the verified manufacturer constants; UV is single-component).

Full derivation, verification tables and the list of values still to confirm
with the supplier: **[`docs/RESIN-FORMULA.md`](./docs/RESIN-FORMULA.md)**.
All product data lives in the `LINERS` / `RESINS` arrays at the top of
`src/App.jsx` — edit there only.

## Deploy

Import the `app/` folder as its own Vercel project (root directory `app`,
framework preset **Vite**, build `npm run build`, output `dist`). Keep it
separate from the `lateral-repairs-web` site.
