#!/usr/bin/env python3
"""
Builds the product pages and the Products mega-menu from one catalogue.

  python3 tools/build-products.py

Writes products/<slug>.html for every item and patches the mega-menu between the
MEGAMENU markers in index.html and in every generated page, so the menu markup
has a single source of truth.

Liner specifications are transcribed from the official technical data sheets in
assets/datasheets/ (issue V2026.1). Do not hand-edit generated pages.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------- #
# Catalogue
# --------------------------------------------------------------------------- #
LINER_NOTE = "Values marked * are nominal. Always confirm against the current data sheet."
GENERIC_NOTE = "Always confirm against the current data sheet before use."

CATALOGUE = [
    {
        "slug": "liners",
        "name": "Liners",
        "blurb": "CIPP hose liners for every diameter and application.",
        "items": [
            {
                "slug": "multiline-flex",
                "name": "MULTIline FLEX",
                "tag": "Drain & lateral lines",
                "lead": "Flexible hose liner for the trenchless rehabilitation of drains and house connections.",
                "summary": "The most flexible liner in the range — negotiates 90° bends and the small "
                           "diameters typical of house connections, from DN 30 upwards.",
                "image": "images/products/flex.jpg",
                "pdf": "assets/datasheets/LR_MULTIline_FLEX.pdf",
                "highlights": ["DN 30 – 250", "3.50 mm wall", "90° bends"],
                "specs": [
                    ("Product code", "FLEX"),
                    ("Length", "50 m; 100 m / 164 ft; 328 ft"),
                    ("Diameter", "30, 40, 50, 60, 65, 70, 75, 80, 100, 125, 150, 200, 225, 250"),
                    ("Wall thickness", "3.50* mm / 0.14* inch"),
                    ("Liner undersized", "5 %, 9 %, 18 %"),
                    ("Heat resistance", "Max. 50 °C / 122 °F"),
                    ("Negotiating bends", "90°"),
                    ("Material", "PES-Plush (knitted) and brushed, with one-sided PU coating"),
                    ("Textile", "Polyester, 450* g/m²"),
                    ("Coating", "One side PU, 250* g/m²"),
                    ("Colour / coating", "White / Transparent"),
                    ("Water penetration", "≤ 500 mbar / ≤ 7.25 psi"),
                    ("Storage", "Protected from light, dry"),
                ],
            },
            {
                "slug": "multiline-core",
                "name": "MULTIline CORE",
                "tag": "Everyday sewer & pipe",
                "lead": "Multi-knitted hose liner for the trenchless inner lining of pipes.",
                "summary": "The dependable all-rounder for standard sewer and pipe rehabilitation, with a "
                           "higher heat resistance than FLEX and the same 90° bend capability.",
                "image": "images/products/core.jpg",
                "pdf": "assets/datasheets/LR_MULTIline_CORE.pdf",
                "highlights": ["DN 70 – 250", "4.50 mm wall", "85 °C"],
                "specs": [
                    ("Product code", "CORE"),
                    ("Length", "50 m; 100 m / 164 ft; 328 ft"),
                    ("Diameter", "70, 80, 100, 125, 150, 200, 225, 250"),
                    ("Wall thickness", "4.50* mm / 0.18* inch"),
                    ("Liner undersized", "13 %"),
                    ("Heat resistance", "Max. 85 °C / 167 °F"),
                    ("Negotiating bends", "Max. 90°"),
                    ("Material", "Multi-knitted fleece with one-sided polypropylene (PP) coating"),
                    ("Textile", "Polyester, 550* g/m²"),
                    ("Coating", "One side PP, 300* g/m²"),
                    ("Colour / coating", "White / Transparent"),
                    ("Water penetration", "≤ 550 mbar / ≤ 7.97 psi"),
                    ("Storage", "Protected from light, dry"),
                ],
            },
            {
                "slug": "multiline-pro-40",
                "name": "MULTIline PRO 4.0 mm",
                "tag": "Advanced technology",
                "lead": "Hose liner for the trenchless inner lining of defective, leaking and statically "
                        "impaired pipes.",
                "summary": "TPU-coated multi-knitted liner for demanding, high-specification work — up to "
                           "DN 300 while still negotiating 90° bends.",
                "image": "images/products/pro.jpg",
                "pdf": "assets/datasheets/LR_MULTIline_PRO_40mm.pdf",
                "highlights": ["DN 70 – 300", "4.00 mm wall", "TPU coating"],
                "specs": [
                    ("Product code", "PRO"),
                    ("Length", "50 m; 100 m / 164 ft; 328 ft"),
                    ("Diameter", "70, 80, 100, 125, 150, 200, 225, 250, 300"),
                    ("Wall thickness", "4.00* mm / 0.16* inch"),
                    ("Liner undersized", "13 %"),
                    ("Heat resistance", "Max. 70 °C / 158 °F"),
                    ("Negotiating bends", "Max. 90°"),
                    ("Material", "Multi (knitted) fleece with one-sided TPU"),
                    ("Textile", "Polyester, 550* g/m²"),
                    ("Coating", "One side TPU, 150* g/m²"),
                    ("Colour / coating", "White / Transparent"),
                    ("Water penetration", "≤ 550 mbar / ≤ 7.97 psi"),
                    ("Storage", "Protected from light, dry"),
                ],
            },
            {
                "slug": "multiline-pro-45",
                "name": "MULTIline PRO 4.5 mm",
                "tag": "Advanced technology",
                "lead": "Hose liner for the trenchless inner lining of defective, leaking and statically "
                        "impaired pipes.",
                "summary": "The thicker-walled PRO for the same DN range — more structural reserve where "
                           "the host pipe is badly degraded.",
                "image": "images/products/pro.jpg",
                "pdf": "assets/datasheets/LR_MULTIline_PRO_45mm.pdf",
                "highlights": ["DN 70 – 300", "4.50 mm wall", "TPU coating"],
                "specs": [
                    ("Product code", "PRO"),
                    ("Length", "50 m; 100 m / 164 ft; 328 ft"),
                    ("Diameter", "70, 80, 100, 125, 150, 200, 225, 250, 300"),
                    ("Wall thickness", "4.50* mm / 0.18* inch"),
                    ("Liner undersized", "13 %"),
                    ("Heat resistance", "Max. 70 °C / 158 °F"),
                    ("Negotiating bends", "Max. 90°"),
                    ("Material", "Multi (knitted) fleece with one-sided TPU"),
                    ("Textile", "Polyester, 550* g/m²"),
                    ("Coating", "One side TPU, 150* g/m²"),
                    ("Colour / coating", "White / Transparent"),
                    ("Water penetration", "≤ 550 mbar / ≤ 7.97 psi"),
                    ("Storage", "Protected from light, dry"),
                ],
            },
            {
                "slug": "multiline-force",
                "name": "MULTIline FORCE",
                "tag": "Structural rehabilitation",
                "lead": "High-strength, reinforced hose liner for the structural rehabilitation of pipes.",
                "summary": "Filament-reinforced liner rated to 100 °C — the choice when the new pipe has to "
                           "carry the load itself.",
                "image": "images/products/force.jpg",
                "pdf": "assets/datasheets/LR_MULTIline_FORCE.pdf",
                "highlights": ["DN 100 – 300", "3.00 mm wall", "100 °C"],
                "specs": [
                    ("Product code", "FORCE"),
                    ("Length", "50 m; 100 m / 164 ft; 328 ft"),
                    ("Diameter", "100 mm – 300 mm / 4 inch – 12 inch"),
                    ("Wall thickness", "3.00 mm / 0.12 inch"),
                    ("Liner undersized", "10 %"),
                    ("Heat resistance", "Max. 100 °C / 212 °F"),
                    ("Negotiating bends", "Max. 45°"),
                    ("Material", "Polyester needle-punched fleece with filament reinforcement and a "
                                 "polypropylene (PP) coating"),
                    ("Textile", "Polyester, 650 g/m²"),
                    ("Coating", "PP, 300 g/m²"),
                    ("Colour / coating", "White / Milky white"),
                    ("Water penetration", "≥ 500 mbar"),
                    ("Storage", "Protected from light, dry"),
                ],
            },
            {
                "slug": "multiline-force-rf",
                "name": "MULTIline FORCE RF",
                "tag": "Large diameter",
                "lead": "High-strength, reinforced hose liner for the structural rehabilitation of pipes.",
                "summary": "The heavy-duty FORCE: a 4.50 mm wall and a heavier textile, reaching DN 600 for "
                           "mains and manhole-to-manhole runs.",
                "image": "images/products/force.jpg",
                "pdf": "assets/datasheets/LR_MULTIline_FORCE_RF.pdf",
                "highlights": ["DN 100 – 600", "4.50 mm wall", "900 g/m²"],
                "specs": [
                    ("Product code", "FORCE"),
                    ("Length", "50 m; 100 m / 164 ft; 328 ft"),
                    ("Diameter", "100 mm – 600 mm / 4 inch – 24 inch"),
                    ("Wall thickness", "4.50 mm / 0.18 inch"),
                    ("Liner undersized", "10 %"),
                    ("Heat resistance", "Max. 100 °C / 212 °F"),
                    ("Negotiating bends", "Max. 45°"),
                    ("Material", "Polyester needle-punched fleece with filament reinforcement and a "
                                 "polypropylene (PP) coating"),
                    ("Textile", "Polyester, 900 g/m²"),
                    ("Coating", "PP, 300 g/m²"),
                    ("Colour / coating", "White / Milky white"),
                    ("Water penetration", "≥ 500 mbar"),
                    ("Storage", "Protected from light, dry"),
                ],
            },
            {
                "slug": "multiline-force-uv",
                "name": "MULTIline FORCE UV",
                "tag": "UV curing",
                "lead": "High-strength, reinforced hose liner for the structural rehabilitation of pipes.",
                "summary": "Reinforced liner with a TPU coating built for UV light-train curing — the crew "
                           "controls exactly when the reline sets, up to DN 600.",
                "image": "images/products/force.jpg",
                "pdf": "assets/datasheets/LR_MULTIline_FORCE_UV.pdf",
                "highlights": ["DN 100 – 600", "3.30 mm wall", "UV cure"],
                "specs": [
                    ("Product code", "FORCEUV"),
                    ("Length", "50 m; 100 m / 164 ft; 328 ft"),
                    ("Diameter", "100 mm – 600 mm / 4 inch – 24 inch"),
                    ("Wall thickness", "3.30 mm / 0.13 inch"),
                    ("Liner undersized", "10 %"),
                    ("Heat resistance", "Max. 80 °C / 176 °F"),
                    ("Negotiating bends", "Max. 45°"),
                    ("Material", "Polyester needle-punched fleece with filament reinforcement and a "
                                 "thermoplastic polyurethane (TPU) coating"),
                    ("Textile", "Polyester, 500 g/m²"),
                    ("Coating", "TPU, 150 g/m²"),
                    ("Colour / coating", "White / Transparent"),
                    ("Storage", "Protected from light, dry"),
                ],
            },
            {
                "slug": "connection-liners",
                "name": "Connection Liners",
                "tag": "Lateral connections",
                "lead": "Flexible polyester knitted hose with thermoplastic coating for the rehabilitation "
                        "of lateral connections.",
                "summary": "Restores lateral and branch connections at 45°, 90° and 180° from DN 50 to "
                           "DN 300 — supplied stitched and sealed, or stitched only.",
                "pdf": "assets/datasheets/LR_Connection_Liners.pdf",
                "highlights": ["DN 50 – 300", "45° · 90° · 180°", "Approx. 3.0 mm"],
                "variants": [
                    {
                        "name": "Stitched & Sealed Connection Liners",
                        "specs": [
                            ("Weight", "Approx. 450 g/m² (DIN EN 29073 T1)"),
                            ("Thickness with coating", "Approx. 3.0 mm (DIN EN 29073 T2)"),
                            ("Pore volume", "Approx. 85 %"),
                            ("Fibers", "Polyester"),
                            ("Coating", "TPU; PUR"),
                            ("Coating thickness", "Approx. 150 μm"),
                            ("Seam type", "Stitched and sealed"),
                            ("Curing", "Ambient · Hot water · Steam mix"),
                            ("Properties", "DN 50 to DN 300 · 45°, 90°, 180° connections"),
                        ],
                    },
                    {
                        "name": "Stitched (not sealed) Connection Liners",
                        "specs": [
                            ("Weight", "Approx. 450 g/m² (DIN EN 29073 T1)"),
                            ("Thickness with coating", "Approx. 3.0 mm (DIN EN 29073 T2)"),
                            ("Pore volume", "Approx. 85 %"),
                            ("Fibers", "Polyester"),
                            ("Coating", "TPU; PUR"),
                            ("Coating thickness", "Approx. 150 μm"),
                            ("Seam type", "Stitched"),
                            ("Curing", "Ambient · Hot water · Steam mix"),
                            ("Properties", "DN 50 to DN 300 · 45°, 90°, 180° connections"),
                        ],
                    },
                ],
                "body": [
                    "The Connection Liner is built for non-pressure pipelines, restoring the junction "
                    "between a lateral and the main with a durable polyester knitted hose under a "
                    "thermoplastic coating. Angles other than 45°, 90° and 180°, and custom sizes, can be "
                    "supplied in consultation with Lateral Repairs.",
                    "The finished quality depends on the resin system used, the inversion pressure and the "
                    "curing pressure — we advise against other resin systems or higher pressures. All "
                    "figures are guideline values determined under laboratory conditions and can differ on "
                    "site.",
                ],
                "note": "Guideline values determined under laboratory conditions; site results can differ.",
            },
        ],
    },
    {
        "slug": "resins",
        "name": "Resins",
        "blurb": "Matched resin systems — the difference between them is working time.",
        "items": [
            {
                "slug": "lr-epoxy-fastcast-15",
                "name": "LR-Epoxy Fastcast 15",
                "tag": "Fastest cure",
                "lead": "Two-component epoxy resin for CIPP lining.",
                "summary": "Our fastest two-part epoxy. Built for small drain and lateral repairs where the "
                           "priority is getting the line back into service the same visit.",
                "highlights": ["2-component epoxy", "Shortest working time", "Drain & lateral repairs"],
                "body": [
                    "Fastcast 15 is the shortest-working-time epoxy in the range. It suits compact jobs — "
                    "house connections, short lateral runs and spot repairs — where the liner can be "
                    "impregnated, inverted and positioned quickly and the customer needs the line back.",
                    "Because the working window is short, plan the wet-out and installation before mixing, "
                    "and mix only what the run needs.",
                ],
            },
            {
                "slug": "lr-epoxy-fastcast-30",
                "name": "LR-Epoxy Fastcast 30",
                "tag": "Longer window",
                "lead": "Two-component epoxy resin for CIPP lining.",
                "summary": "The same fast-cast chemistry with a longer working window — extra time to "
                           "impregnate and place the liner, while still curing quickly on site.",
                "highlights": ["2-component epoxy", "Longer working time", "General lining"],
                "body": [
                    "Fastcast 30 gives crews more room than Fastcast 15 without moving to a long pot-life "
                    "system. It is the general-purpose choice for everyday lateral and sewer lining where "
                    "the run is longer or access makes the installation slower.",
                ],
            },
            {
                "slug": "lr-120-plus",
                "name": "LR-120+",
                "tag": "Longest working time",
                "lead": "Long pot-life epoxy resin for large-diameter and long installations.",
                "summary": "Our longest working time, for large-diameter and manhole-to-manhole runs where a "
                           "big liner has to be soaked and installed without racing the clock.",
                "highlights": ["2-component epoxy", "Extended pot life", "Large diameter / long runs"],
                "body": [
                    "LR-120+ is formulated for the jobs where volume is the constraint: long liners, large "
                    "diameters and manhole-to-manhole rehabilitation. The extended pot life lets a crew "
                    "wet out a large liner properly and still have time to invert and position it.",
                ],
            },
            {
                "slug": "lr-uv-resin",
                "name": "LR-UV-Resin",
                "tag": "Light cured",
                "lead": "Light-cured resin for UV liner systems.",
                "summary": "Stays workable until the UV light train is switched on, so the crew decides "
                           "exactly when curing starts.",
                "highlights": ["Single component", "Cure on demand", "For UV liner systems"],
                "body": [
                    "With a UV system there is no mixing clock. The impregnated liner stays workable until "
                    "the light train is drawn through it, which gives complete control over timing — useful "
                    "on complex installations and long runs.",
                    "Pair with MULTIline FORCE UV, which carries the TPU coating intended for UV curing.",
                ],
            },
            {
                "slug": "lr-silicate-resin",
                "name": "LR Silicate Resin",
                "tag": "Silicate system",
                "lead": "Water glass / polyisocyanate two-component synthetic resin system for lining.",
                "summary": "Supplied as an \"A\" component — Winter, Summer or W01 Fast — cured with the "
                           "waterglass \"B\" hardener, so the system can be matched to site temperature and "
                           "the required set speed.",
                "highlights": ["2-component (A + B)", "Winter · Summer · W01 Fast", "Waterglass hardener"],
                "body": [
                    "The silicate range is a water glass / polyisocyanate based two-component synthetic "
                    "resin. The \"A\" component is chosen for the conditions — Type W (Winter), Type Summer "
                    "or Type W01 (Fast) — and is combined with the LR Silicate Resin Waterglass Hardener as "
                    "the \"B\" component.",
                    "Confirm the exact grade and mixing ratio against the labels on the kit you receive. "
                    "The safety data sheets below carry the full hazard, handling and first-aid information "
                    "and should be read before use.",
                ],
                "docs": [
                    {"label": "LR Silicate Resin Type W · Winter", "sub": "Safety data sheet · \"A\" component",
                     "file": "assets/datasheets/LR_Silicate_Resin_Winter_SDS.pdf"},
                    {"label": "LR Silicate Resin Type Summer", "sub": "Safety data sheet · \"A\" component",
                     "file": "assets/datasheets/LR_Silicate_Resin_Summer_SDS.pdf"},
                    {"label": "LR Silicate Resin Type W01 · Fast", "sub": "Safety data sheet · \"A\" component",
                     "file": "assets/datasheets/LR_Silicate_Resin_W01_Fast_SDS.pdf"},
                    {"label": "LR Silicate Resin Waterglass · Hardener", "sub": "Safety data sheet · \"B\" component",
                     "file": "assets/datasheets/LR_Silicate_Resin_Waterglass_Hardener_SDS.pdf"},
                ],
            },
        ],
    },
    {
        "slug": "consumables",
        "name": "Other consumables",
        "blurb": "Everything else the crew needs to complete the installation.",
        "items": [
            {
                "slug": "calibration-hoses",
                "name": "Calibration hoses",
                "tag": "Installation equipment",
                "lead": "PVC-coated polyester calibration hose in light and heavy duty constructions.",
                "summary": "The calibration hose carries the pressure that holds the impregnated liner "
                           "against the host pipe while it cures. Both constructions work with the common "
                           "resin systems — UV vinyl ester, silicate and epoxy.",
                "highlights": ["Light duty · 50 °C", "Heavy duty · 80 °C", "50 m / 100 m rolls"],
                "variants": [
                    {
                        "name": "Welded LD — light duty",
                        "specs": [
                            ("Material", "Welded LD — available Transparent or Violet"),
                            ("Base fabric", "PVC-coated polyester"),
                            ("Seam", "Overlapped and heat-welded seam (light duty)"),
                            ("Compatible resins", "UV Vinyl Ester · Silicate · Epoxy"),
                            ("Standard roll lengths", "50 m, 100 m"),
                            ("Maximum working temperature", "50 °C"),
                        ],
                        "matrix": {
                            "head": ["Pipe diameter (mm)", "50", "70", "100", "125", "150", "200", "225", "250", "300"],
                            "row": ["Max. recommended pressure (bar)", "0.80", "0.68", "0.55", "0.51", "0.47",
                                    "0.45", "0.44", "0.42", "0.40"],
                        },
                    },
                    {
                        "name": "Stitched & Welded HD — heavy duty",
                        "specs": [
                            ("Material", "Stitched & Welded HD — available Transparent or Orange"),
                            ("Base fabric", "PVC-coated polyester"),
                            ("Seam", "Overlapped, stitched and tape-welded seam (heavy duty)"),
                            ("Compatible resins", "UV Vinyl Ester · Silicate · Epoxy"),
                            ("Standard roll lengths", "50 m, 100 m"),
                            ("Maximum working temperature", "80 °C"),
                        ],
                        "matrix": {
                            "head": ["Pipe diameter (mm)", "100", "125", "150", "200", "225", "250", "300"],
                            "row": ["Max. recommended pressure (bar)", "1.70", "1.60", "1.40", "1.20", "1.00",
                                    "0.80", "0.60"],
                        },
                    },
                ],
                "body": [
                    "Duty class is chosen from the working pressure and the diameter of the run: the heavy "
                    "duty construction carries roughly three times the pressure of the light duty hose at "
                    "DN 100 and tolerates a higher curing temperature.",
                    "All hose is supplied for single use only; re-use is at the customer's risk. In use the "
                    "hose must be supported outside the pipe, kept off grit and gravel, and never walked on. "
                    "Because of sizing at manufacture, please state whether the hose is intended as a "
                    "calibration hose or a pre-liner when ordering.",
                ],
                "docs": [
                    {"label": "Calibration Hose Welded — Transparent", "sub": "Technical data sheet · light duty",
                     "file": "assets/datasheets/LR_Calibration_Hose_Heat_Welded_MD.pdf"},
                    {"label": "Calibration Hose Welded · Violet", "sub": "Technical data sheet · light duty",
                     "file": "assets/datasheets/LR_Calibration_Hose_Welded_Violet.pdf"},
                    {"label": "Calibration Hose Stitched & Welded — Transparent", "sub": "Technical data sheet · heavy duty",
                     "file": "assets/datasheets/LR_Calibration_Hose_Stitched_Welded.pdf"},
                    {"label": "Calibration Hose Stitched & Welded — Orange", "sub": "Technical data sheet · heavy duty",
                     "file": "assets/datasheets/LR_Calibration_Hose_Stitched_Welded_Orange.pdf"},
                ],
            },
            {
                "slug": "patch-repair-kit",
                "name": "Patch Repair Kit",
                "tag": "Spot repairs",
                "lead": "Complete kit for a single localised pipe repair.",
                "summary": "A boxed, pre-measured kit containing everything needed for one patch repair — "
                           "glass mat, two-part resin, tools and protection.",
                "image": "images/gallery/patch-kit.jpg",
                "highlights": ["Pre-measured glass mat", "Two-part resin pack", "100 × 550 mm WR"],
                "body": [
                    "Each kit is packed for a single repair so nothing has to be measured on site. Contents: "
                    "pre-measured glass mat, protective gloves, disposable protective ground sheet, resin "
                    "spreader, plastic cable ties and wire ties, packer protection hose and a two-part "
                    "resin pack.",
                ],
            },
            {
                "slug": "glassfiber-complex-1050",
                "name": "Glassfiber Complex 1050",
                "tag": "Reinforcement",
                "lead": "E-CR glass-fibre reinforcement complex for structural pipe rehabilitation and "
                        "CIPP lining.",
                "summary": "A two-layer stitched complex — chopped strand mat backed by woven roving — "
                           "used where the finished laminate has to carry structural load.",
                "pdf": "assets/datasheets/LR_Glassfiber_Complex_1050.pdf",
                "highlights": ["E-CR glass", "1050 g/m² ± 8 %", "125 / 250 cm width"],
                "specs": [
                    ("Glass composition", "E-CR Glass"),
                    ("Weight per unit area", "1050 g/m² ± 8 % (deviation from nominal)"),
                    ("1st layer — Chopped Strand Mat", "500 g/m²"),
                    ("2nd layer — Woven Roving", "Warp 0°: 150 g/m² · Weft 90°: 410 g/m²"),
                    ("Bonding", "Stitching"),
                    ("Sewing thread (polyester)", "≤ 15 g/m²"),
                    ("Moisture content", "< 0.15 %"),
                    ("Edges", "Trimmed"),
                    ("Width", "125 cm / 250 cm"),
                    ("Coupling agent", "Silane"),
                    ("Tube diameter, internal", "70 mm"),
                ],
                "body": [
                    "Condition the material for 24 hours at room temperature in the application area "
                    "before use. Store it in its original packaging, keep it dry, and keep the storage "
                    "temperature below 35 °C.",
                    "Rolls are packed in stretch film and supplied on pallets. Other roll widths, tube "
                    "diameters and lengths are available on request. Resin quantity can be calculated with "
                    "the free Lateral Repairs app.",
                ],
                "note": "Always confirm against the current data sheet before use.",
            },
            {
                "slug": "end-cap-glue",
                "name": "End Cap Glue",
                "tag": "Ancillary",
                "lead": "Solvent-borne, toluene-free special contact adhesive for industrial and "
                        "professional use.",
                "summary": "A contact adhesive that bonds on contact and reaches full strength in about "
                           "two days — suited to rubber, leather, gasket, sheet, moulding, metal and "
                           "lining materials.",
                "pdf": "assets/datasheets/LR_End_Cap_Glue.pdf",
                "highlights": ["Cures 5 – 15 min", "−40 °C to +75 °C", "Approx. 4 m² / l"],
                "specs": [
                    ("Application temperature", "+10 °C – +40 °C"),
                    ("Using temperature", "min. +5 °C"),
                    ("Temperature resistance", "−40 °C – +75 °C *"),
                    ("Curing time", "5 – 15 min (depending on conditions)"),
                    ("Open time", "10 – 40 min"),
                    ("Density", "0.83 g/ml"),
                    ("Dosage", "approx. 4 m² / l"),
                    ("Colour", "Yellowish"),
                    ("Phase", "Slightly yellowish liquid synthetic rubber solution"),
                    ("Tools", "Brush, roller or spray gun"),
                    ("Packaging", "Steel cans · 1, 3, 10, 20, 200, 1000 L"),
                    ("Cleaning", "Acetone (product and tools)"),
                    ("Storage stability", "12 months · +5 – +25 °C, dry"),
                    ("Fire", "Highly flammable"),
                    ("Transport", "ADR UN 1133, class 3.1"),
                ],
                "body": [
                    "Surfaces must be clean, dry and free from grease and dust, and may be coarse-ground. "
                    "Apply a thin, even layer to both surfaces with a brush or roller — for spray-gun use "
                    "it can be thinned with 5–20 % acetone. Let it dry for 15–40 minutes depending on "
                    "conditions, then press the surfaces firmly together, checking for air bubbles.",
                    "Over-dried surfaces can be reactivated with heat; if heated, press together while "
                    "still warm. The bond holds immediately and develops full strength in about two days. "
                    "The dried adhesive is freeze-resistant.",
                    "The product is highly flammable and harmful — read the safety data sheet before use "
                    "and dispose of residues as hazardous waste; the cans are recyclable.",
                ],
                "note": "* Heat resistance of the dry seam is approx. +75 °C. Read the safety data sheet "
                        "before use.",
            },
        ],
    },
]


def esc(s):
    return html.escape(str(s), quote=True)


# --------------------------------------------------------------------------- #
# Mega-menu
# --------------------------------------------------------------------------- #
def menu_html(base=""):
    cols = []
    panels = []
    for i, cat in enumerate(CATALOGUE):
        active = " is-active" if i == 0 else ""
        cols.append(
            f'<button type="button" class="mega__cat{active}" role="tab" '
            f'aria-selected="{"true" if i == 0 else "false"}" aria-controls="mega-{cat["slug"]}" '
            f'data-mega-cat="{cat["slug"]}">'
            f'<span>{esc(cat["name"])}</span>'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="m9 6 6 6-6 6"/></svg>'
            f"</button>"
        )
        links = "".join(
            f'<a class="mega__item" href="{base}products/{it["slug"]}.html">'
            f'<b>{esc(it["name"])}</b><span>{esc(it["tag"])}</span></a>'
            for it in cat["items"]
        )
        panels.append(
            f'<div class="mega__panel{active}" id="mega-{cat["slug"]}" role="tabpanel" '
            f'data-mega-panel="{cat["slug"]}">'
            f'<p class="mega__blurb">{esc(cat["blurb"])}</p>'
            f'<div class="mega__grid">{links}</div>'
            f"</div>"
        )
    return (
        '<div class="mega" id="megaMenu" hidden>\n'
        '        <div class="mega__inner">\n'
        f'          <div class="mega__cats" role="tablist" aria-label="Product categories">{"".join(cols)}</div>\n'
        f'          <div class="mega__panels">{"".join(panels)}</div>\n'
        "        </div>\n"
        "      </div>"
    )


# --------------------------------------------------------------------------- #
# Mobile drawer (lives outside <header> so the nav's backdrop-filter cannot
# become its containing block — that bug collapsed the old fullscreen menu)
# --------------------------------------------------------------------------- #
NAV_LINKS = [
    ("technology", "Technology"),
    ("group", "Group"),
    ("certifications", "Quality"),
    ("app", "App"),
    ("contact", "Contact"),
]


def drawer_html(base=""):
    home = f"{base}index.html" if base else "index.html"
    groups = []
    for i, cat in enumerate(CATALOGUE):
        items = "".join(
            f'<a href="{base}products/{it["slug"]}.html">{esc(it["name"])}'
            f'<span>{esc(it["tag"])}</span></a>'
            for it in cat["items"]
        )
        groups.append(
            f'<div class="dgroup" data-dgroup>'
            f'<button type="button" class="dgroup__btn" aria-expanded="false">'
            f'<span>{esc(cat["name"])}</span>'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>'
            f"</button>"
            f'<div class="dgroup__items"><div class="dgroup__inner">{items}</div></div>'
            f"</div>"
        )
    links = "".join(f'<a href="{home}#{a}">{esc(b)}</a>' for a, b in NAV_LINKS)
    return (
        '<button class="drawer__scrim" id="drawerScrim" aria-label="Close menu" tabindex="-1"></button>\n'
        '  <aside class="drawer" id="drawer" aria-label="Menu" aria-hidden="true">\n'
        '    <div class="drawer__head">\n'
        f'      <a href="{home}" class="drawer__brand" aria-label="Lateral Repairs home">\n'
        f'        <img src="{base}images/logo.svg" alt="" />\n'
        f'        <img src="{base}images/wordmark.png" alt="Lateral Repairs" class="drawer__word" />\n'
        "      </a>\n"
        '      <button type="button" class="drawer__close" id="drawerClose" aria-label="Close menu">\n'
        '        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>\n'
        "      </button>\n"
        "    </div>\n"
        '    <div class="drawer__body">\n'
        '      <p class="drawer__label">Products</p>\n'
        f'      {"".join(groups)}\n'
        f'      <nav class="drawer__links">{links}</nav>\n'
        f'      <a href="{home}#contact" class="btn btn-primary drawer__cta">Get a quote</a>\n'
        "    </div>\n"
        "  </aside>"
    )


# --------------------------------------------------------------------------- #
# Interactive catalogue browser on the home page
# --------------------------------------------------------------------------- #
def catalog_html():
    opts, panels = [], []
    for i, cat in enumerate(CATALOGUE):
        sel = "true" if i == 0 else "false"
        opts.append(
            f'<li role="option" aria-selected="{sel}" tabindex="-1" data-pick="{cat["slug"]}">'
            f'<b>{esc(cat["name"])}</b><span>{esc(cat["blurb"])}</span></li>'
        )
        cards = []
        for it in cat["items"]:
            media = (
                f'<span class="pcard__media"><img src="{it["image"]}" alt="" loading="lazy" /></span>'
                if it.get("image")
                else '<span class="pcard__media pcard__media--blank" aria-hidden="true">'
                     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">'
                     '<path d="M3 12h18M12 3v18"/><circle cx="12" cy="12" r="9"/></svg></span>'
            )
            docs = len(it.get("docs", [])) or (1 if it.get("pdf") else 0)
            badge = f'<span class="pcard__doc">{docs} PDF</span>' if docs else ""
            cards.append(
                f'<a class="pcard" href="products/{it["slug"]}.html">'
                f"{media}"
                f'<span class="pcard__body">'
                f'<span class="pcard__tag">{esc(it["tag"])}{badge}</span>'
                f'<b>{esc(it["name"])}</b>'
                f'<span class="pcard__sum">{esc(it["summary"])}</span>'
                f'<span class="pcard__go">View details'
                f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                f'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
                f"</span></span></a>"
            )
        panels.append(
            f'<div class="catalog__panel{" is-active" if i == 0 else ""}" '
            f'data-cat-panel="{cat["slug"]}">{"".join(cards)}</div>'
        )
    first = CATALOGUE[0]
    return (
        '<div class="catalog" id="catalog">\n'
        '        <div class="picker" data-picker>\n'
        '          <button type="button" class="picker__btn" id="pickerBtn" aria-haspopup="listbox" '
        'aria-expanded="false">\n'
        '            <span class="picker__meta"><small>Category</small>'
        f'<b id="pickerLabel">{esc(first["name"])}</b></span>\n'
        '            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>\n'
        "          </button>\n"
        f'          <ul class="picker__list" role="listbox" aria-label="Product category">{"".join(opts)}</ul>\n'
        "        </div>\n"
        f'        <div class="catalog__panels">{"".join(panels)}</div>\n'
        "      </div>"
    )


# --------------------------------------------------------------------------- #
# Product page
# --------------------------------------------------------------------------- #
PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>{name} — Lateral Repairs</title>
  <meta name="description" content="{meta}" />
  <meta name="theme-color" content="#070608" />
  <link rel="icon" type="image/png" sizes="192x192" href="../images/icon-192.png" />
  <link rel="canonical" href="https://lateral-repairs-website.vercel.app/products/{slug}" />
  <meta property="og:type" content="product" />
  <meta property="og:title" content="{name} — Lateral Repairs" />
  <meta property="og:description" content="{meta}" />
  <link rel="stylesheet" href="../assets/fonts/fonts.css?v=14" />
  <link rel="stylesheet" href="../assets/css/styles.css?v=14" />
</head>
<body>

  <header class="nav scrolled" id="nav">
    <a href="../index.html" class="nav__logo" aria-label="Lateral Repairs home">
      <img src="../images/logo.svg" alt="" class="brand__mark" />
      <img src="../images/wordmark.png" alt="Lateral Repairs" class="brand__wordmark" />
    </a>
    <nav class="nav__links" id="navLinks" aria-label="Primary">
      <div class="nav__has-mega" data-mega-root>
        <a href="../index.html#products" class="nav__mega-trigger" id="megaTrigger"
           aria-haspopup="true" aria-expanded="false">Products
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
        </a>
        <!-- MEGAMENU:START -->
        <!-- MEGAMENU:END -->
      </div>
      <a href="../index.html#technology">Technology</a>
      <a href="../index.html#group">Group</a>
      <a href="../index.html#certifications">Quality</a>
      <a href="../index.html#app">App</a>
      <a href="../index.html#contact">Contact</a>
    </nav>
    <div class="nav__cta">
      <a href="../index.html#contact" class="btn btn-ghost">Get a quote</a>
      <button class="nav__burger" id="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </header>

  <!-- DRAWER:START -->
  <!-- DRAWER:END -->

  <main class="pdp">
    <div class="container">
      <nav class="pdp__crumbs" aria-label="Breadcrumb">
        <a href="../index.html">Home</a> <span>/</span>
        <a href="../index.html#products">Products</a> <span>/</span>
        <span class="pdp__crumb-cat">{cat}</span>
      </nav>

      <div class="pdp__head">
        <div class="pdp__intro">
          <span class="product__tag">{tag}</span>
          <h1>{name}</h1>
          <p class="pdp__lead">{lead}</p>
          <p class="pdp__summary">{summary}</p>
          <ul class="pdp__highlights">{highlights}</ul>
          <div class="pdp__actions">{actions}</div>
        </div>
        {media}
      </div>

      {content}

      <div class="pdp__cta">
        <div>
          <h2>Need this for a project?</h2>
          <p>Tell us the diameter, length and application and our technical team will confirm the right
             liner and resin combination.</p>
        </div>
        <a href="../index.html#contact" class="btn btn-primary">Request a quote
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        </a>
      </div>
    </div>
  </main>

  <footer>
    <div class="container">
      <div class="legal">
        <div class="reg">
          <b>UAB&nbsp;"Lateral&nbsp;repairs"</b> &nbsp;·&nbsp; Company code: 304403126 &nbsp;·&nbsp; VAT: LT100010469717<br>
          Paberžių g. 5, LT-72328 Tauragė, Lithuania
        </div>
        <div class="copy">
          <a href="../privacy.html">Privacy Policy</a> · <a href="../cookies.html">Cookie Policy</a> ·
          <a href="../index.html">Home</a>
        </div>
      </div>
    </div>
  </footer>

  <script src="../assets/js/main.js?v=14" defer></script>
</body>
</html>
"""


def build_page(cat, item):
    highlights = "".join(f"<li>{esc(h)}</li>" for h in item.get("highlights", []))

    pdf_icon = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<path d="M14 2v6h6"/></svg>'
    )
    actions = []
    if item.get("pdf"):
        actions.append(
            f'<a class="btn btn-primary" href="../{item["pdf"]}" target="_blank" rel="noopener">'
            f"{pdf_icon} Technical data sheet</a>"
        )
    elif item.get("docs"):
        n = len(item["docs"])
        actions.append(
            f'<a class="btn btn-primary" href="#documents">{pdf_icon} '
            f'{n} document{"s" if n != 1 else ""}</a>'
        )
    actions.append('<a class="btn btn-ghost" href="../index.html#contact">Ask a question</a>')

    media = ""
    if item.get("image"):
        media = (
            f'<figure class="pdp__media"><img src="../{item["image"]}" alt="{esc(item["name"])}" /></figure>'
        )

    # footnote: only mention asterisks when the table actually uses them
    note = item.get("note")
    if not note:
        values = [v for _, v in item.get("specs", [])]
        for var in item.get("variants", []):
            values += [v for _, v in var["specs"]]
        note = LINER_NOTE if any("*" in str(v) for v in values) else GENERIC_NOTE

    blocks = []
    if item.get("specs"):
        rows = "".join(
            f"<tr><th scope=\"row\">{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in item["specs"]
        )
        blocks.append(
            '<section class="pdp__specs">'
            "<h2>Technical data</h2>"
            f'<div class="legal-table-wrap"><table class="legal-table pdp__table"><tbody>{rows}</tbody></table></div>'
            f'<p class="pdp__note">{esc(note)}</p>'
            "</section>"
        )
    if item.get("variants"):
        parts = []
        for v in item["variants"]:
            rows = "".join(
                f'<tr><th scope="row">{esc(k)}</th><td>{esc(val)}</td></tr>' for k, val in v["specs"]
            )
            block = (
                f'<h3 class="pdp__variant-name">{esc(v["name"])}</h3>'
                f'<div class="legal-table-wrap"><table class="legal-table pdp__table"><tbody>{rows}'
                f"</tbody></table></div>"
            )
            if v.get("matrix"):
                head = "".join(f"<th>{esc(h)}</th>" for h in v["matrix"]["head"])
                cells = "".join(
                    (f'<th scope="row">{esc(c)}</th>' if i == 0 else f"<td>{esc(c)}</td>")
                    for i, c in enumerate(v["matrix"]["row"])
                )
                block += (
                    '<div class="legal-table-wrap"><table class="legal-table pdp__matrix">'
                    f"<thead><tr>{head}</tr></thead><tbody><tr>{cells}</tr></tbody></table></div>"
                )
            parts.append(f'<div class="pdp__variant">{block}</div>')
        blocks.append(
            '<section class="pdp__specs"><h2>Technical data</h2>' + "".join(parts)
            + f'<p class="pdp__note">{esc(note)}</p></section>'
        )

    if item.get("body"):
        paras = "".join(f"<p>{esc(p)}</p>" for p in item["body"])
        blocks.append(f'<section class="pdp__body"><h2>About this product</h2>{paras}</section>')

    if item.get("docs"):
        cards = "".join(
            f'<a class="doc-item" href="../{d["file"]}" target="_blank" rel="noopener">'
            f'<span class="doc-item__ic">{pdf_icon}</span>'
            f'<span class="doc-item__txt"><b>{esc(d["label"])}</b><span>{esc(d["sub"])}</span></span>'
            f'<svg class="doc-item__go" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M7 17 17 7M9 7h8v8"/></svg></a>'
            for d in item["docs"]
        )
        blocks.append(
            '<section class="pdp__docs" id="documents"><h2>Documents</h2>'
            f'<div class="doc-grid">{cards}</div></section>'
        )

    others = [i for i in cat["items"] if i["slug"] != item["slug"]]
    if others:
        links = "".join(
            f'<a class="mega__item" href="{o["slug"]}.html"><b>{esc(o["name"])}</b>'
            f'<span>{esc(o["tag"])}</span></a>'
            for o in others
        )
        blocks.append(
            f'<section class="pdp__related"><h2>Other {esc(cat["name"]).lower()}</h2>'
            f'<div class="mega__grid">{links}</div></section>'
        )

    page = PAGE.format(
        name=esc(item["name"]),
        slug=item["slug"],
        cat=esc(cat["name"]),
        tag=esc(item["tag"]),
        lead=esc(item["lead"]),
        summary=esc(item["summary"]),
        meta=esc(f'{item["name"]} — {item["lead"]} Lateral Repairs CIPP products.'),
        highlights=highlights,
        actions="".join(actions),
        media=media,
        content="".join(blocks),
    )
    return inject_menu(page, base="../")


# --------------------------------------------------------------------------- #
# Menu injection
# --------------------------------------------------------------------------- #
def inject(text, name, content, indent):
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    if start not in text:
        raise SystemExit(f"{name} markers missing")
    return re.sub(
        re.escape(start) + r".*?" + re.escape(end),
        lambda _: f"{start}\n{indent}{content}\n{indent}{end}",
        text,
        flags=re.S,
    )


def inject_menu(text, base=""):
    text = inject(text, "MEGAMENU", menu_html(base), "        ")
    return inject(text, "DRAWER", drawer_html(base), "  ")


def main():
    out = ROOT / "products"
    out.mkdir(exist_ok=True)
    n = 0
    for cat in CATALOGUE:
        for item in cat["items"]:
            (out / f'{item["slug"]}.html').write_text(build_page(cat, item), encoding="utf-8")
            n += 1

    index = ROOT / "index.html"
    src = inject_menu(index.read_text(encoding="utf-8"), base="")
    src = inject(src, "CATALOG", catalog_html(), "      ")
    index.write_text(src, encoding="utf-8")

    print(f"generated {n} product pages -> products/")
    print("patched mega-menu, drawer and catalogue in index.html")


if __name__ == "__main__":
    main()
