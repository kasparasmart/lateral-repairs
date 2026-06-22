# Lateral Repairs — App (Resin Calculator + Datasheets)

The installer-facing tool: a resin **mix calculator** (metric & imperial) and a
**technical datasheet** viewer. React 19 + Vite 8. This is a **separate product**
from the marketing website in the repo root — deploy it as its own project.

## Run locally

```bash
cd app
npm install
npm run dev      # http://localhost:5173
npm run build    # outputs to app/dist
```

## How the calculator works

```
total resin volume  ≈  π · D · L · t · saturation      (lib/calc.js → estimateResinLitres)
resin / hardener    =  total split by the resin's own datasheet ratio   (splitMix)
```

**The bug this rebuild fixes:** the old app split *every* resin with one fixed
hardener fraction (~`0.757` resin / `0.243` hardener ≈ 100:32). Now each resin
uses its **own** ratio from `src/data/resins.js`:

| Resin | Ratio (by weight) |
|-------|-------------------|
| Fastcast 15 | 100:30 |
| Fastcast 30 | 100:33 |
| Fastcast Mega | 100:33 |
| UV Resin | single component (no hardener) |

## ⚠️ Verify before field use

All product data lives in **one file**: `src/data/resins.js`. Values flagged
`verified: false` are typical placeholders pending the datasheets:

- **Liner wall thicknesses** (`LINERS[].wallMm`) — drive the volume estimate.
- **`SATURATION_FACTOR`** — fraction of the felt annulus filled with resin.

The mix **ratios** are confirmed; the total **volume** is a geometric estimate —
confirm against the datasheet and allow for wastage.

## Datasheets

Drop PDFs into `public/datasheets/` using the filenames listed in
`DATASHEETS` (`src/data/resins.js`). They appear in the Datasheets tab
automatically (the app probes for each file on load).

## Deploy

Import **this `app/` folder** as its own Vercel project (root directory: `app`,
framework preset **Vite**, build `npm run build`, output `dist`). Keep it
separate from the `lateral-repairs-web` site so neither overwrites the other.
