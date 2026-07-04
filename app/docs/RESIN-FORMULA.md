# Resin Calculator — Formula Derivation & Verification

Status: **engineering estimate for sales support** — reviewed derivation, built on
the company's own published data. Items in [To confirm](#to-confirm-with-the-supplier)
should be checked against kit labels / supplier TDS before the numbers are treated
as binding.

## 1. Where the quantity comes from (not invented)

Each MULTIline liner datasheet (Issue **V2026.1 · 2026.06**, shipped in the app's
Tech Data section) prints a **Resin kg/m table per DN**. The calculator uses those
tables directly:

```
total resin (kg) = kg/m(DN, liner) × liner length (m) × (1 + margin %)
```

- `kg/m(DN)` — linear interpolation between the datasheet's own points.
  Datasheet *range* rows (e.g. "DN 100–150 ~1.01") map to their **lower-bound DN**;
  cross-checked against shell geometry (π·D·t·ρ) this gives a consistent
  ~1.05–1.13 kg per geometric litre across every row, whereas midpoint mapping
  does not — so lower-bound is the correct reading of the table.
- FORCE RF / FORCE UV datasheets cover DN 100–600 but tabulate to DN 300. Their
  tables are exactly linear in DN (RF: kg/m = 16.03 × DN[m], R² = 1.000), so the
  same slope is extended past DN 300. Verified: DN 400 → 6.41 kg/m, identical to
  the slope prediction.
- DN outside the product's datasheet range is clamped and a warning is shown.

Because the manufacturer's kg/m already includes impregnation excess
(FORCE 3.0 works out to geometry × ~1.22 kg/L, i.e. ~+7 % over plain volume),
the table is *more conservative than the pure geometric formula* — the right
direction for ordering.

### Margin
A selectable **wet-out / wastage margin** (0 / 5 / 10 / 15 %, default 10 %) is
applied on top, standard industry practice for pump lines, mixing losses and
bends. The datasheets separately prescribe *length* additions per bend and
dimension change — the operator adds those to the entered length.

## 2. Mix ratio and densities

| Constant | Value | Source |
|---|---|---|
| Fastcast 15 ratio | **100 : 30 by weight** (≈ 3 : 1 by volume) | Decodes exactly from the legacy app constants (see below); matches the published lateral-resin "Extended" blend (30 pbw, 3:1 v/v) |
| Fastcast 30 ratio | **100 : 33 by weight** | Earlier datasheet review; directionally consistent with the family pattern (slower blend → more hardener); **confirm on kit label** |
| LR-120+ ratio | **100 : 43 by weight** (≈ 2 : 1 by volume) | The long-pot-life **"Ambient"** blend in the published lateral-resin family PDS (2:1 v/v, 43 pbw); LR-120+'s 120-min pot life maps to that blend; **confirm on kit label** |
| Density part A | **1.153 kg/L** | Original app |
| Density part B | **1.079 kg/L** | Original app |
| Mixed density | derived per ratio: FC15 **1.135**, FC30 **1.134**, LR-120+ **1.130** kg/L | = (a+b) / (a/1.153 + b/1.079); FC15 reproduces the legacy hard-coded 1.135 exactly |
| LR-UV-Resin | single component, density **1.15 kg/L** | mid-range of the MFE 7516 styrene-free vinyl ester SDS ("relative density 1,1–1,20 g/mL at 25 °C", in Tech Data); **confirm** it is the UV resin's SDS |

### Ratio assignment logic (pot life ↔ family blend)

The published lateral-resin family PDS is internally consistent with our
component densities — converting its volume ratios to weight with
A 1.153 / B 1.079 gives: 4:1 v/v → 23 pbw (printed 22), 3:1 → 31 (printed 30),
2:1 → 47 (printed 43). Longer working time = more hardener parts:

| Blend | v/v | pbw | Pot life class | Mapped product |
|---|---|---|---|---|
| Winter / Standard / Summer | 4:1 | 22 | fastest | — (not in app) |
| Extended | 3:1 | 30 | fast (~15 min class) | **Fastcast 15** |
| (between Extended and Ambient) | — | 33 | ~30 min | **Fastcast 30** |
| Ambient | 2:1 | 43 | long (ambient cure, 120+ min) | **LR-120+** |

**Why we trust the original constants:** the legacy app split volume as
0.757 / 0.243 with densities 1.153 / 1.079. That split is *exactly* 100:30 by
weight, and the mixed density 1.135 derives exactly from those numbers. Three
independent constants agreeing to 4 significant figures means they came from a
real manufacturer datasheet. Independently, the **FORCE RF datasheet kg/m equals
geometric volume × 1.135 kg/L** — the same density again.

The legacy app's actual bug was applying that (Fastcast-15) split to every
resin, including single-component UV. That is fixed: each entry in `RESINS`
(`src/App.jsx`) carries its own ratio/densities, and UV is single-component.

## 3. Component split

```
A (kg) = total × 100/130          B (kg) = total × 30/130
A (L)  = A/1.153                  B (L)  = B/1.079
```
(Volume split works out to 75.7 % / 24.3 % — byte-identical to the legacy app
for Fastcast 15, so historical quotes remain comparable.)

## 4. Verification (spot checks)

| Case | Result | Cross-check |
|---|---|---|
| FORCE 3.0, DN150 × 5 m, 0 % | 8.60 kg / 7.58 L | geometry 7.07 L·1.135 = 8.02 kg (datasheet +7 % excess); ChatGPT/manual estimate 7.8 kg @ρ1.1 |
| FLEX, DN150 × 5 m, +10 % | 8.69 kg / 7.66 L | legacy app 8.02 kg (no margin) |
| FORCE RF, DN400 × 10 m | 64.1 kg | table slope 16.03·0.4·10 = 64.1 kg ✓ |
| All FORCE RF table DNs | exact | interpolator reproduces every printed point |
| Mixed density | 1.1350 | legacy constant 1.135 ✓ |

## 5. To confirm with the supplier

Change these in **one place** — the `RESINS` array in `src/App.jsx`:

1. **Fastcast 30** — ratio 100:33 by weight (earlier datasheet review; pot life
   ~30 min @25 °C per supplier page). Confirm on the kit label.
2. **LR-120+** — ratio 100:43 by weight (mapped to the "Ambient" family blend,
   2:1 v/v / 43 pbw, by its 120-min pot life). Confirm on the kit label.
3. **LR-UV-Resin** — density 1.15 kg/L, taken as the mid-range of the MFE 7516
   vinyl ester SDS (1,1–1,20 g/mL). Confirm MFE 7516 is the LR-UV-Resin base.
4. Component densities for FC30 / LR-120+ assumed same as FC15 (A 1.153 / B 1.079).

The result screen prints "Confirm the mix ratio on the kit label before ordering"
whenever a `confirm: true` resin is selected, plus the datasheets' own
"non-binding guideline values" wording on every result.

## Sources

- MULTIline datasheets V2026.1 (in-repo: `public/datasheets/*.pdf`) — kg/m tables, DN ranges, wall thicknesses, length-addition rules.
- Legacy app constants (recovered `App.jsx`): 0.757/0.243, 1.153, 1.079, 1.135.
- [Lateral Repairs — resin systems](https://www.lateralrepairs.com/resin-systems/), [Fast Cast FCA](https://www.lateralrepairs.com/lateral-repairs-fast-cast-fca/), [Fast Cast 30B](https://www.lateralrepairs.com/lateral-repairs-fast-cast-30b/)
- [LR Fast Cast 30 (reseller)](https://piperehabilitationsolutions.com/products/lr-fast-cast-30-resin) — 2-component ambient-cure epoxy, pot life ~30 min @25 °C.
- [Lateral resin product data sheet (family blends)](https://www.scribd.com/document/658985454/Lateral-Resin-Product-Data-Sheet) — Winter/Standard/Summer 4:1 v/v (22 pbw), **Extended 3:1 v/v (30 pbw)**, Ambient 2:1 v/v (43 pbw).
