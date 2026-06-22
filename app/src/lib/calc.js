// ─────────────────────────────────────────────────────────────────────────
// Calculator core. Pure functions, no React — easy to reason about & test.
//
// THE FIX: the previous app split every resin with one fixed hardener
// fraction (~0.757 resin / 0.243 hardener ≈ 100:32). Here the split is
// derived from each resin's OWN datasheet ratio, so Fastcast 15 (100:30),
// Fastcast 30 / Mega (100:33) and the single-component UV resin each come
// out correctly.
// ─────────────────────────────────────────────────────────────────────────

import { SATURATION_FACTOR } from '../data/resins.js'

// Unit conversions
export const IN_TO_MM = 25.4
export const FT_TO_M = 0.3048
export const L_TO_GAL = 0.264172 // US gallons

/**
 * Split a total mix amount into resin + hardener using the resin's own ratio.
 * Works for any unit (kg, L, parts) because the ratio is dimensionless.
 * @param {number} total   total combined amount
 * @param {{resin:number, hardener:number}} mix  ratio by weight, e.g. {resin:100,hardener:30}
 * @returns {{resin:number, hardener:number}}
 */
export function splitMix(total, mix) {
  const parts = mix.resin + mix.hardener
  if (parts <= 0 || total <= 0) return { resin: 0, hardener: 0 }
  const resin = (total * mix.resin) / parts
  const hardener = (total * mix.hardener) / parts
  return { resin, hardener }
}

/**
 * Estimate the total resin volume (litres) to wet-out a liner.
 * V = π · D · L · t · saturation
 * @param {object} p
 * @param {number} p.diameterMm  internal/nominal diameter in mm
 * @param {number} p.lengthM     liner length in metres
 * @param {number} p.wallMm      liner wall thickness in mm
 * @param {number} [p.saturation]
 * @returns {number} litres
 */
export function estimateResinLitres({ diameterMm, lengthM, wallMm, saturation = SATURATION_FACTOR }) {
  if (!(diameterMm > 0 && lengthM > 0 && wallMm > 0)) return 0
  const D = diameterMm / 1000 // m
  const t = wallMm / 1000 // m
  const volumeM3 = Math.PI * D * lengthM * t * saturation
  return volumeM3 * 1000 // litres
}

export const litresToGallons = (l) => l * L_TO_GAL
export const round = (n, dp = 2) => {
  const f = 10 ** dp
  return Math.round((n + Number.EPSILON) * f) / f
}

// Format a ratio object as "100:30" (or "single component" for UV).
export function ratioLabel(mix) {
  if (!mix.hardener) return 'single component'
  return `${mix.resin}:${mix.hardener}`
}
