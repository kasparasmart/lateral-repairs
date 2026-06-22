// ─────────────────────────────────────────────────────────────────────────
// RESIN SPECIFICATIONS — single source of truth for the calculator.
//
// `mix` is the resin:hardener ratio BY WEIGHT exactly as printed on the
// technical datasheet (e.g. 100:30 means 100 parts resin to 30 parts
// hardener). This is the safety-critical number and drives the split.
//
// `verified: true`  → ratio confirmed from datasheet / prior agreement.
// `verified: false` → placeholder, MUST be checked against the datasheet
//                     before field use (surfaced as a warning in the UI).
//
// To add or correct a resin, edit this file only — the calculator and the
// datasheet list both read from here.
// ─────────────────────────────────────────────────────────────────────────

export const RESINS = [
  {
    id: 'fc15',
    name: 'LR-Epoxy Fastcast 15',
    short: 'Fastcast 15',
    type: 'epoxy',
    mix: { resin: 100, hardener: 30 }, // 100:30 by weight
    verified: true,
    potLife: '~15 min',
    notes: 'Fast-cure epoxy for shorter installs.',
  },
  {
    id: 'fc30',
    name: 'LR-Epoxy Fastcast 30',
    short: 'Fastcast 30',
    type: 'epoxy',
    mix: { resin: 100, hardener: 33 }, // 100:33 by weight
    verified: true,
    potLife: '~30 min',
    notes: 'Standard-cure epoxy for general CIPP work.',
  },
  {
    id: 'mega',
    name: 'LR-Epoxy Fastcast Mega',
    short: 'Fastcast Mega',
    type: 'epoxy',
    mix: { resin: 100, hardener: 33 }, // 100:33 by weight
    verified: true,
    potLife: 'extended',
    notes: 'Large-volume / long-pot-life epoxy for big diameters & long shots.',
  },
  {
    id: 'uv',
    name: 'LR-UV-Resin',
    short: 'UV Resin',
    type: 'uv',
    mix: { resin: 100, hardener: 0 }, // single component, UV cured — no hardener
    singleComponent: true,
    verified: true,
    potLife: 'light-stable until cured',
    notes: 'Single-component, UV-cured. No hardener — total = resin only.',
  },
]

// Liner presets feed the optional volume estimator. Wall thickness drives the
// resin volume estimate (V ≈ π · D · L · t · saturation). Thicknesses here are
// typical values — VERIFY each against the liner datasheet.
export const LINERS = [
  { id: 'drainplus', name: 'LR Drain Plus', wallMm: 3.0, verified: false },
  { id: 'megaliner', name: 'LR Megaliner', wallMm: 4.0, verified: false },
  { id: 'custom', name: 'Custom / enter wall thickness', wallMm: 3.0, verified: true },
]

// Saturation factor: fraction of the felt annulus volume filled by resin at
// full wet-out. 1.0 = the simple geometric volume. Reproduces the website's
// worked example (DN150 × 5 m, 3.14 mm effective wall → ~7.4 L). VERIFY.
export const SATURATION_FACTOR = 1.0

// Datasheets shown in the Datasheets tab. Drop the matching PDF into
// public/datasheets/ and set `file`. Entries with no file show as "coming soon".
export const DATASHEETS = [
  { id: 'fc15', title: 'LR-Epoxy Fastcast 15', file: 'datasheets/fastcast-15.pdf' },
  { id: 'fc30', title: 'LR-Epoxy Fastcast 30', file: 'datasheets/fastcast-30.pdf' },
  { id: 'mega', title: 'LR-Epoxy Fastcast Mega', file: 'datasheets/fastcast-mega.pdf' },
  { id: 'uv', title: 'LR-UV-Resin', file: 'datasheets/uv-resin.pdf' },
  { id: 'megaliner', title: 'LR Megaliner', file: 'datasheets/megaliner.pdf' },
  { id: 'drainplus', title: 'LR Drain Plus liner', file: 'datasheets/drain-plus.pdf' },
  { id: 'seals', title: 'Seals & accessories', file: 'datasheets/seals.pdf' },
]
