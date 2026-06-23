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

## ⚠️ The resin formula — known issue (not yet fixed here)

This is a faithful restore, so it keeps the **original** calculator behaviour,
including the bug. In `src/App.jsx` → `CalcScreen.calculate()`:

```js
const compAL = totalL * 0.757;   // Resin A  — same split for EVERY resin
const compBL = totalL * 0.243;   // Hardener — same split for EVERY resin (≈100:32)
```

The selected resin (Fastcast 15 / Fastcast 30 / LR-120+ / UV) does **not** change
the math — it's only printed as a label. The intended fix is a per-resin ratio,
e.g. FC15 = 100:30, FC30 = 100:33, UV = single component. Applying it correctly
needs the exact ratio + component densities from each datasheet (pending).

## Deploy

Import the `app/` folder as its own Vercel project (root directory `app`,
framework preset **Vite**, build `npm run build`, output `dist`). Keep it
separate from the `lateral-repairs-web` site.
