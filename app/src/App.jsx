import { useState } from "react";
import {
  Zap,
  Clock,
  FileText,
  Shield,
  Image,
  Phone,
  Video,
  Mail,
  MapPin,
  Globe,
  RotateCcw,
  Check,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";

// ─── THEME ───────────────────────────────────────────────────────────────────
const C = {
  bg: "#0a0a0a",
  card: "#111111",
  cardHover: "#181818",
  border: "#222",
  pink: "#e91e8c",
  pinkDim: "#9b1260",
  cyan: "#00bcd4",
  green: "#4caf50",
  red: "#e53935",
  purple: "#7c4dff",
  gold: "#ffa000",
  text: "#ffffff",
  muted: "#666",
  label: "#888",
};

// ─── STATIC IMAGE URLS ───────────────────────────────────────────────────────
const IMG = {
  logo:         "/images/logo.jpg",
  backwallLevi: "/images/backwall-levi.jpg",
  backwallDesni:"/images/backwall-desni.jpg",
  backwall400:  "/images/backwall-400.jpg",
  backwall425:  "/images/backwall-425.jpg",
  topWall:      "/images/top-wall.jpg",
  banner:       "/images/banner.jpg",
};

const styles = {
  app: {
    background: C.bg,
    minHeight: "100vh",
    fontFamily: "'Rajdhani', 'Oswald', sans-serif",
    color: C.text,
    maxWidth: 420,
    margin: "0 auto",
    position: "relative",
    overflow: "hidden",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: "10px 16px",
    borderBottom: `1px solid ${C.border}`,
    background: C.bg,
    position: "sticky",
    top: 0,
    zIndex: 100,
  },
  headerLogoWrap: {
    height: 44,
    width: 100,
    flexShrink: 0,
    overflow: "hidden",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  headerTitle: { lineHeight: 1.1 },
  brandName: { fontSize: 18, fontWeight: 700, letterSpacing: 2, fontStyle: "italic" },
  brandSub: { fontSize: 10, color: C.muted, letterSpacing: 3 },
  backBtn: {
    background: "none",
    border: "none",
    color: C.muted,
    cursor: "pointer",
    padding: "0 8px 0 0",
    lineHeight: 1,
    display: "flex",
    alignItems: "center",
  },
  pageTitle: { fontSize: 16, fontWeight: 700, letterSpacing: 3, fontStyle: "italic", flex: 1 },
  body: { padding: "20px 16px" },
  // Home
  heroBanner: {
    background: C.pinkDim,
    borderRadius: 6,
    padding: "16px 20px",
    display: "flex",
    alignItems: "center",
    gap: 16,
    marginBottom: 20,
    cursor: "pointer",
  },
  heroBannerText: { flex: 1 },
  heroBannerLabel: { fontSize: 10, color: "rgba(255,255,255,0.6)", letterSpacing: 3 },
  heroBannerCTA: { fontSize: 20, fontWeight: 700, letterSpacing: 2 },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 12,
  },
  gridCard: {
    background: C.card,
    border: `1px solid ${C.border}`,
    borderRadius: 6,
    padding: "28px 16px 20px",
    display: "flex",
    flexDirection: "column",
    gap: 12,
    cursor: "pointer",
    transition: "background 0.15s",
    minHeight: 140,
    position: "relative",
  },
  gridLabel: { fontSize: 14, fontWeight: 700, letterSpacing: 2, marginTop: 4 },
  // Section page
  sectionTitle: { fontSize: 28, fontWeight: 700, letterSpacing: 1, marginBottom: 2 },
  sectionSub: { fontSize: 11, color: C.muted, letterSpacing: 3, marginBottom: 0 },
  divider: { height: 2, background: C.pink, margin: "12px 0 24px", borderRadius: 1 },
  listItem: {
    background: C.card,
    border: `1px solid ${C.border}`,
    borderRadius: 6,
    padding: "14px 16px",
    display: "flex",
    alignItems: "center",
    gap: 14,
    marginBottom: 10,
    cursor: "pointer",
  },
  listIcon: {
    width: 52,
    height: 52,
    background: "#1a1a1a",
    borderRadius: 6,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  listText: { flex: 1 },
  listTitle: { fontSize: 15, fontWeight: 700, marginBottom: 2 },
  listSub: { fontSize: 10, color: C.muted, letterSpacing: 2 },
  // Calculator
  calcTitle: { fontSize: 24, fontWeight: 700, letterSpacing: 1, marginBottom: 20, display: "flex", alignItems: "center", gap: 10 },
  label: { fontSize: 12, color: C.label, letterSpacing: 3, marginBottom: 8, marginTop: 16, display: "block" },
  toggleRow: { display: "flex", gap: 0, marginBottom: 4 },
  toggleBtn: (active, color = C.cyan) => ({
    flex: 1,
    padding: "12px 0",
    border: `1px solid ${active ? color : C.border}`,
    background: active ? `${color}22` : C.card,
    color: active ? color : C.muted,
    fontFamily: "inherit",
    fontSize: 13,
    fontWeight: 700,
    letterSpacing: 2,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
  }),
  input: {
    width: "100%",
    background: C.card,
    border: `1px solid ${C.border}`,
    borderRadius: 4,
    padding: "14px 16px",
    color: C.text,
    fontFamily: "inherit",
    fontSize: 16,
    outline: "none",
    boxSizing: "border-box",
  },
  selectBox: {
    width: "100%",
    background: C.card,
    border: `1px solid ${C.border}`,
    borderRadius: 4,
    padding: "14px 16px",
    color: C.text,
    fontFamily: "inherit",
    fontSize: 15,
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  dropdown: {
    background: "#2a2a2a",
    borderRadius: 12,
    overflow: "hidden",
    marginTop: 4,
    boxShadow: "0 8px 32px rgba(0,0,0,0.6)",
  },
  dropItem: () => ({
    padding: "16px 20px",
    borderBottom: `1px solid ${C.border}`,
    cursor: "pointer",
    fontSize: 16,
    fontWeight: 500,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    background: "transparent",
    color: C.text,
  }),
  calcBtn: (color) => ({
    width: "100%",
    padding: "18px",
    background: color,
    border: "none",
    borderRadius: 4,
    color: "#fff",
    fontFamily: "inherit",
    fontSize: 16,
    fontWeight: 700,
    letterSpacing: 3,
    cursor: "pointer",
    marginTop: 12,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  }),
  resultBox: {
    background: "#0d2a0d",
    border: `1px solid ${C.green}44`,
    borderRadius: 6,
    padding: 16,
    marginTop: 16,
  },
  resultRow: { display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: `1px solid ${C.border}` },
  resultLabel: { color: C.muted, fontSize: 13, letterSpacing: 1 },
  resultValue: { fontWeight: 700, fontSize: 15, color: C.green },
  // Cure Timer
  cureTitle: { fontSize: 24, fontWeight: 700, display: "flex", alignItems: "center", gap: 10, marginBottom: 20 },
  cureResult: {
    background: "#0a2030",
    border: `1px solid ${C.cyan}44`,
    borderRadius: 6,
    padding: 20,
    marginTop: 16,
    textAlign: "center",
  },
  // Contact
  contactCard: {
    background: C.card,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    padding: 24,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 20,
  },
  phoneCircle: {
    width: 80,
    height: 80,
    borderRadius: "50%",
    background: "#1a1a1a",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 4,
  },
  contactTitle: { fontSize: 32, fontWeight: 900, letterSpacing: 2, textAlign: "center" },
  contactSub: { fontSize: 11, color: C.muted, letterSpacing: 4, textAlign: "center" },
  contactRow: {
    width: "100%",
    background: "#1a1a1a",
    border: `1px solid ${C.border}`,
    borderRadius: 6,
    padding: "16px 20px",
    display: "flex",
    alignItems: "center",
    gap: 14,
  },
  contactRowLabel: { fontSize: 10, color: C.muted, letterSpacing: 2 },
  contactRowValue: { fontSize: 16, fontWeight: 600 },
  visitBtn: {
    width: "100%",
    padding: 18,
    background: "#fff",
    color: "#000",
    border: "none",
    borderRadius: 6,
    fontSize: 15,
    fontWeight: 700,
    letterSpacing: 3,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
  },
  versionText: { fontSize: 11, color: C.muted, textAlign: "center", letterSpacing: 2, marginTop: 16 },
  updateBtn: {
    background: "#1a1a1a",
    border: `1px solid ${C.border}`,
    color: C.muted,
    padding: "12px 32px",
    borderRadius: 4,
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: 3,
    cursor: "pointer",
    fontFamily: "inherit",
    display: "block",
    margin: "20px auto 0",
  },
  uploadBox: {
    border: `2px dashed ${C.border}`,
    borderRadius: 6,
    padding: "40px 20px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 12,
    marginTop: 10,
    cursor: "pointer",
  },
};

// ─── DATA ────────────────────────────────────────────────────────────────────
// ─── RESIN CALCULATION DATA ──────────────────────────────────────────────────
// Quantity basis: the official "Resin kg/m" tables printed in the MULTIline
// technical datasheets (Issue V2026.1 · 2026.06) — the same PDFs shipped in
// the Tech Data section. Points are [DN (mm), kg mixed resin per metre];
// datasheet range rows map to their lower-bound DN (cross-checked against
// shell geometry π·D·t within ±5 %). Between points: linear interpolation.
// FORCE RF / FORCE UV datasheets cover DN 100–600 and their tables are linear
// in DN, so the same slope extends past the last printed point.
// Full derivation + verification: docs/RESIN-FORMULA.md.
const LINERS = [
  { name: "MULTIline FLEX",            wall: 3.5, dn: [30, 250],
    kgm: [[30, 0.32], [50, 0.51], [70, 0.73], [100, 1.01], [125, 1.24], [150, 1.58], [200, 2.08], [225, 2.31], [250, 2.58]] },
  { name: "MULTIline PRO 4.5 mm",      wall: 4.5, dn: [70, 300],
    kgm: [[70, 0.82], [100, 1.15], [150, 1.70], [200, 2.45], [250, 2.99]] },
  { name: "MULTIline PRO 5.5 mm",      wall: 5.5, dn: [70, 300],
    kgm: [[70, 0.95], [100, 1.32], [150, 1.88], [200, 2.65], [250, 3.25]] },
  { name: "MULTIline CORE",            wall: 4.5, dn: [70, 350],
    kgm: [[70, 0.94], [100, 1.25], [150, 1.90], [200, 2.60], [250, 3.10], [300, 3.80]] },
  { name: "MULTIline FORCE 3.0 mm",    wall: 3.0, dn: [100, 300],
    kgm: [[100, 1.15], [125, 1.44], [150, 1.72], [200, 2.30], [225, 2.60], [250, 2.90], [300, 3.21]] },
  { name: "MULTIline FORCE RF 4.5 mm", wall: 4.5, dn: [100, 600],
    kgm: [[100, 1.60], [125, 2.00], [150, 2.41], [200, 3.21], [225, 3.61], [250, 4.01], [300, 4.81]] },
  { name: "MULTIline FORCE UV",        wall: 3.3, dn: [100, 600],
    kgm: [[100, 1.15], [125, 1.44], [150, 1.72], [200, 2.30], [225, 2.60], [250, 2.90], [300, 3.21]] },
];
const LINER_TYPES = LINERS.map((l) => l.name);

// Mix data. 100:30 by weight (≈3:1 by volume) with component densities
// A 1.153 / B 1.079 kg/L are the manufacturer constants from the original
// app — exactly self-consistent (mixed density 1.135 kg/L) and matching the
// published "Extended" lateral-resin blend (30 pbw hardener). UV resin is
// single-component. Entries flagged `confirm` must be checked against the
// kit label before quoting — this array is the only place to change them.
const RESINS = [
  // FC15: 100:30 pbw — decodes exactly from the legacy app constants (see docs).
  { name: "LR-Epoxy Fastcast 15", ratio: [100, 30], densA: 1.153, densB: 1.079 },
  // FC30: 100:33 pbw — from the earlier datasheet review; slower blend = more
  // hardener, consistent with the family pattern (22 → 30 → 43 pbw).
  { name: "LR-Epoxy Fastcast 30", ratio: [100, 33], densA: 1.153, densB: 1.079, confirm: true },
  // LR-120+: 100:43 pbw — the long-pot-life "Ambient" family blend
  // (2:1 by volume / 43 pbw); 120+ min pot life matches that blend.
  { name: "LR-120+",              ratio: [100, 43], densA: 1.153, densB: 1.079, confirm: true },
  // Density: mid-range of the MFE 7516 styrene-free vinyl ester SDS
  // ("relative density 1.1–1.20 g/mL at 25 °C", in Tech Data).
  { name: "LR-UV-Resin",          single: true, dens: 1.15, confirm: true },
];
const RESIN_SYSTEMS = RESINS.map((r) => r.name);

// Wet-out / wastage margin applied on top of the datasheet quantity.
const EXTRA_OPTIONS = ["0 %", "5 %", "10 %", "15 %"];

// kg of mixed resin per metre at a given DN — linear interpolation between
// datasheet points, linear extrapolation past the last point (used only by
// the DN 100–600 FORCE liners; DN is clamped to the product range first).
function kgPerMetre(liner, dnMm) {
  const pts = liner.kgm;
  if (dnMm <= pts[0][0]) return pts[0][1];
  for (let i = 1; i < pts.length; i++) {
    if (dnMm <= pts[i][0]) {
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
      return y0 + ((y1 - y0) * (dnMm - x0)) / (x1 - x0);
    }
  }
  const [x0, y0] = pts[pts.length - 2], [x1, y1] = pts[pts.length - 1];
  return y1 + ((y1 - y0) * (dnMm - x1)) / (x1 - x0);
}

const mixedDensity = (r) =>
  r.single ? r.dens : (r.ratio[0] + r.ratio[1]) / (r.ratio[0] / r.densA + r.ratio[1] / r.densB);

const DATASHEETS = [
  { name: "Complete pack — all documents", file: "/datasheets/lr-technical-data-complete.pdf" },
  { name: "MULTIline PRO 4.5 mm",      file: "/datasheets/multiline-pro-4-5mm.pdf" },
  { name: "MULTIline PRO 5.5 mm",      file: "/datasheets/multiline-pro-5-5mm.pdf" },
  { name: "MULTIline FLEX",            file: "/datasheets/multiline-flex.pdf" },
  { name: "MULTIline CORE",            file: "/datasheets/multiline-core.pdf" },
  { name: "MULTIline FORCE 3.0 mm",    file: "/datasheets/multiline-force-3-0mm.pdf" },
  { name: "MULTIline FORCE RF 4.5 mm", file: "/datasheets/multiline-force-rf-4-5mm.pdf" },
  { name: "MULTIline FORCE UV",        file: "/datasheets/multiline-force-uv.pdf" },
  { name: "Calibration Hose Welded · Violet (LD)",  file: "/datasheets/calibration-hose-welded-violet-ld.pdf" },
  { name: "Calibration Hose Welded (MD)",           file: "/datasheets/calibration-hose-welded-md.pdf" },
  { name: "Calibration Hose Stitched & Welded (HD)", file: "/datasheets/calibration-hose-stitched-welded-hd.pdf" },
  { name: "Glassfiber Complex 1050",   file: "/datasheets/glassfiber-complex-1050.pdf" },
  { name: "End Cap Glue",              file: "/datasheets/end-cap-glue.pdf" },
  { name: "MFE 7516 Vinyl Ester — SDS", file: "/datasheets/mfe7516-vinyl-ester-sds.pdf" },
  { name: "Silicate Resin Waterglass Hardener — SDS", file: "/datasheets/silicate-resin-waterglass-hardener-sds.pdf" },
  { name: "Silicate Resin W01 Fast — SDS",            file: "/datasheets/silicate-resin-w01-fast-sds.pdf" },
  { name: "Silicate Resin Winter — SDS",               file: "/datasheets/silicate-resin-winter-sds.pdf" },
  { name: "Silicate Resin Summer — SDS",               file: "/datasheets/silicate-resin-summer-sds.pdf" },
];

// Certifying / testing bodies shown as logos only (no certificate uploaded).
const CERT_BODIES = [
  { name: "Eurofins", src: "/certificates/logos/eurofins.png" },
  { name: "NSF", src: "/certificates/logos/nsf.png" },
  { name: "SINTEF", src: "/certificates/logos/sintef.jpeg" },
  { name: "WRC", src: "/certificates/logos/wrc.jpg" },
];

const MEDIA_ITEMS = [
  { name: "Get Closer to Our Environment", type: "YOUTUBE VIDEO", isVideo: true, color: C.red, url: "https://youtu.be/vocDgeuguTs?si=PjYW2sM12gtUxUrj" },
];

// ─── SECTION IMAGE COMPONENT ─────────────────────────────────────────────────

function SectionPhoto({ src, url, maxHeight, style }) {
  return (
    <div
      onClick={() => url && window.open(url, "_blank")}
      style={{
        borderRadius: 8,
        overflow: "hidden",
        cursor: url ? "pointer" : "default",
        boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
        maxHeight: maxHeight || undefined,
        ...style,
      }}
    >
      <img src={src} alt="" style={{ width: "100%", display: "block" }} />
    </div>
  );
}

// ─── COMPONENTS ──────────────────────────────────────────────────────────────

function SelectDropdown({ options, value, onChange }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ position: "relative" }}>
      <div
        style={{ ...styles.selectBox, borderColor: open ? C.pink : C.border }}
        onClick={() => setOpen(!open)}
      >
        <span style={{ fontWeight: 600 }}>{value}</span>
        <ChevronRight
          size={14}
          color={C.pink}
          style={{ transform: open ? "rotate(90deg)" : "rotate(0deg)", transition: "transform 0.15s" }}
        />
      </div>
      {open && (
        <div style={{ ...styles.dropdown, position: "absolute", left: 0, right: 0, zIndex: 50 }}>
          {options.map((opt) => (
            <div
              key={opt}
              style={styles.dropItem(opt === value)}
              onClick={() => { onChange(opt); setOpen(false); }}
            >
              <span>{opt}</span>
              <span style={{
                width: 20, height: 20, borderRadius: "50%",
                border: `2px solid ${opt === value ? C.cyan : C.muted}`,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                {opt === value && (
                  <span style={{ width: 10, height: 10, borderRadius: "50%", background: C.cyan, display: "block" }} />
                )}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── SCREENS ─────────────────────────────────────────────────────────────────

function HomeScreen({ navigate }) {
  return (
    <div style={styles.body}>
      {/* Hero — Top Wall: wide landscape brand strip */}
      <SectionPhoto
        src={IMG.topWall}
        url={IMG.topWall}
        style={{ marginBottom: 16 }}
      />

      {/* Download banner */}
      {/* Feature grid */}
      <div style={styles.grid}>
        {[
          { key: "calc",    Icon: Zap,      iconColor: C.pink,   label: "MIX CALC",     accent: C.pink },
          { key: "cure",    Icon: Clock,    iconColor: C.cyan,   label: "CURE TIME",    accent: null },
          { key: "data",    Icon: FileText, iconColor: C.gold,   label: "TECH DATA",    accent: null },
          { key: "certs",   Icon: Shield,   iconColor: C.purple, label: "CERTIFICATES", accent: null },
          { key: "media",   Icon: Image,    iconColor: C.gold,   label: "MEDIA",        accent: null },
          { key: "contact", Icon: Phone,    iconColor: C.green,  label: "CONTACT",      accent: null },
        ].map(({ key, Icon, iconColor, label, accent }) => (
          <div
            key={key}
            style={styles.gridCard}
            onClick={() => navigate(key)}
            onMouseEnter={(e) => e.currentTarget.style.background = C.cardHover}
            onMouseLeave={(e) => e.currentTarget.style.background = C.card}
          >
            <Icon size={36} color={iconColor} style={{ filter: `drop-shadow(0 0 8px ${iconColor})` }} />
            {accent && <div style={{ width: 28, height: 3, background: accent, borderRadius: 2 }} />}
            <div style={styles.gridLabel}>{label}</div>
          </div>
        ))}
      </div>

      {/* Hashtag backwall — full length at the bottom */}
      <SectionPhoto
        src={IMG.backwallDesni}
        url={IMG.backwallDesni}
        style={{ marginTop: 20 }}
      />
    </div>
  );
}

function CalcScreen() {
  const [units, setUnits] = useState("METRIC");
  const [linerType, setLinerType] = useState("MULTIline FLEX");
  const [resin, setResin] = useState("LR-Epoxy Fastcast 15");
  const [dn, setDn] = useState("150");
  const [extra, setExtra] = useState("10 %");
  const [length, setLength] = useState("5");
  const [result, setResult] = useState(null);

  const liner = LINERS.find((l) => l.name === linerType);
  const isMetric = units === "METRIC";

  function calculate() {
    const rs = RESINS.find((r) => r.name === resin);
    const dnMm = (parseFloat(dn) || 0) * (isMetric ? 1 : 25.4);
    const lenM = (parseFloat(length) || 0) * (isMetric ? 1 : 0.3048);
    if (dnMm <= 0 || lenM <= 0) return;
    const extraPct = parseFloat(extra) || 0;

    // Quantity from the liner datasheet's resin table (kg/m at this DN),
    // clamped to the product's DN range, plus the selected margin.
    const dnClamped = Math.min(Math.max(dnMm, liner.dn[0]), liner.dn[1]);
    const kgm = kgPerMetre(liner, dnClamped);
    const totalKg = kgm * lenM * (1 + extraPct / 100);
    const totalL = totalKg / mixedDensity(rs);

    // Component split by the resin system's mix ratio (by weight).
    let compAKg, compBKg, compAL, compBL;
    if (rs.single) {
      compAKg = totalKg; compBKg = 0; compAL = totalL; compBL = 0;
    } else {
      const [a, b] = rs.ratio;
      compAKg = (totalKg * a) / (a + b);
      compBKg = (totalKg * b) / (a + b);
      compAL = compAKg / rs.densA;
      compBL = compBKg / rs.densB;
    }

    const r2 = (n) => parseFloat(n.toFixed(2));
    setResult({
      linerType, resin, rs, extraPct,
      dn: parseFloat(dn) || 0, dnMm: r2(dnMm), dnClamped: r2(dnClamped),
      dnOutOfRange: dnMm !== dnClamped,
      length: parseFloat(length) || 0, wall: liner.wall, kgm: r2(kgm),
      totalKg: r2(totalKg), totalL: r2(totalL),
      compAKg: r2(compAKg), compBKg: r2(compBKg), compAL: r2(compAL), compBL: r2(compBL),
    });
  }

  function reset() {
    setDn("150"); setExtra("10 %"); setLength("5"); setResult(null);
  }

  // Output formatting in the selected unit system.
  const fmtW = (kg) => (isMetric ? `${kg} kg` : `${(kg * 2.20462).toFixed(2)} lbs`);
  const fmtV = (l) => (isMetric ? `${l} L` : `${(l * 0.264172).toFixed(2)} gal`);

  if (result) {
    const resinA = result.resin + " A";
    const resinB = result.resin + " B";
    const divider = { height: 1, background: "#2a2a2a", margin: "4px 0" };
    const sectionHdr = { fontSize: 15, fontWeight: 600, color: C.text, padding: "14px 0 8px", letterSpacing: 0.5 };
    const row = { display: "flex", justifyContent: "space-between", alignItems: "flex-start", padding: "5px 0" };
    const rowLbl = { color: C.muted, fontSize: 14 };
    const rowVal = { color: C.text, fontSize: 14, fontWeight: 400, textAlign: "right" };
    const compLbl = { fontSize: 14, fontWeight: 700, color: C.text, padding: "8px 0 2px" };
    const subLbl  = { fontSize: 12, color: C.muted, paddingBottom: 4 };
    return (
      <div style={styles.body}>
        {/* Your Entries */}
        <div style={sectionHdr}>Your Entries</div>
        <div style={divider} />
        {[
          ["Liner type",       result.linerType],
          ["Resin system",     result.resin],
          ["Liner DN",         result.dn + (units === "METRIC" ? " mm" : " in")],
          ["Wall thickness",   result.wall.toFixed(1) + " mm"],
          ["Liner lenght",     result.length + (units === "METRIC" ? " m" : " ft")],
          ["Extra margin",     "+" + result.extraPct + " %"],
          ["Mix ratio",        result.rs.single ? "Single component" : result.rs.ratio.join(":") + " by weight"],
        ].map(([l, v]) => (
          <div key={l} style={row}>
            <span style={rowLbl}>{l}</span>
            <span style={rowVal}>{v}</span>
          </div>
        ))}

        {result.dnOutOfRange && (
          <div style={{ color: "#ffb020", fontSize: 12, padding: "6px 0" }}>
            ⚠ DN {result.dnMm} mm is outside the {result.linerType} range
            ({LINERS.find((l) => l.name === result.linerType).dn.join("–")} mm) —
            calculated at DN {result.dnClamped} mm.
          </div>
        )}

        {/* Total */}
        <div style={{ ...divider, marginTop: 12 }} />
        <div style={sectionHdr}>Resultant total amount of resin</div>
        <div style={divider} />
        <div style={row}>
          <span style={rowLbl}>Resin mixture Total</span>
          <span style={rowVal}>{fmtV(result.totalL)}</span>
        </div>
        <div style={{ ...row, paddingTop: 0 }}>
          <span style={rowLbl} />
          <span style={rowVal}>{fmtW(result.totalKg)}</span>
        </div>

        {result.rs.single ? (
          <>
            <div style={{ ...divider, marginTop: 12 }} />
            <div style={sectionHdr}>Component</div>
            <div style={divider} />
            <div style={compLbl}>Resin (single component — no hardener)</div>
            <div style={{ ...row, paddingTop: 0 }}>
              <span style={subLbl}>{result.resin}</span>
              <span style={rowVal}>{fmtV(result.compAL)} · {fmtW(result.compAKg)}</span>
            </div>
          </>
        ) : (
          <>
            {/* Volume */}
            <div style={{ ...divider, marginTop: 12 }} />
            <div style={sectionHdr}>Volume</div>
            <div style={divider} />
            <div style={compLbl}>Resin</div>
            <div style={{ ...row, paddingTop: 0 }}>
              <span style={subLbl}>{resinA}</span>
              <span style={rowVal}>{fmtV(result.compAL)}</span>
            </div>
            <div style={compLbl}>Hardener</div>
            <div style={{ ...row, paddingTop: 0 }}>
              <span style={subLbl}>{resinB}</span>
              <span style={rowVal}>{fmtV(result.compBL)}</span>
            </div>

            {/* Weight */}
            <div style={{ ...divider, marginTop: 12 }} />
            <div style={sectionHdr}>Weight</div>
            <div style={divider} />
            <div style={compLbl}>Resin</div>
            <div style={{ ...row, paddingTop: 0 }}>
              <span style={subLbl}>{resinA}</span>
              <span style={rowVal}>{fmtW(result.compAKg)}</span>
            </div>
            <div style={compLbl}>Hardener</div>
            <div style={{ ...row, paddingTop: 0 }}>
              <span style={subLbl}>{resinB}</span>
              <span style={rowVal}>{fmtW(result.compBKg)}</span>
            </div>
          </>
        )}

        <div style={{ ...divider, marginTop: 12 }} />
        <div style={{ color: C.muted, fontSize: 11, lineHeight: 1.5, padding: "10px 0 0" }}>
          Basis: {result.linerType} datasheet (V2026.1) resin table — {result.kgm} kg/m at
          DN {result.dnClamped} mm, +{result.extraPct} % wet-out margin.
          {result.rs.confirm && " Confirm the mix ratio on the kit label before ordering."}
          {" "}Non-binding guideline values; add length for bends and dimension changes per the
          liner datasheet.
        </div>

        <div style={{ height: 24 }} />
        <button style={styles.calcBtn(C.pink)} onClick={reset}>
          <RotateCcw size={16} /> NEW CALCULATION
        </button>
      </div>
    );
  }

  return (
    <div style={styles.body}>
      <SectionPhoto
        src={IMG.backwall400}
        url="/images/explore-trenchless.pdf"
        style={{ marginBottom: 20 }}
      />
      <div style={styles.calcTitle}>
        <Zap size={28} color={C.pink} style={{ filter: `drop-shadow(0 0 6px ${C.pink})` }} />
        <span>RESIN CALCULATOR</span>
      </div>

      <span style={styles.label}>UNITS</span>
      <div style={styles.toggleRow}>
        {["METRIC", "IMPERIAL"].map((u) => (
          <button key={u} style={styles.toggleBtn(units === u, C.text)} onClick={() => setUnits(u)}>{u}</button>
        ))}
      </div>

      <span style={styles.label}>LINER TYPE</span>
      <SelectDropdown options={LINER_TYPES} value={linerType} onChange={setLinerType} />

      <span style={styles.label}>RESIN SYSTEM</span>
      <SelectDropdown options={RESIN_SYSTEMS} value={resin} onChange={setResin} />

      <span style={styles.label}>LINER DN ({isMetric ? "MM" : "IN"})</span>
      <input style={styles.input} value={dn} onChange={(e) => setDn(e.target.value)} placeholder={isMetric ? "150" : "6"} type="number" />
      <div style={{ color: C.muted, fontSize: 11, marginTop: 6 }}>
        {liner.name}: DN {liner.dn[0]}–{liner.dn[1]} mm · wall {liner.wall.toFixed(1)} mm (from datasheet)
      </div>

      <span style={styles.label}>LINER LENGTH ({isMetric ? "M" : "FT"})</span>
      <input style={styles.input} value={length} onChange={(e) => setLength(e.target.value)} placeholder={isMetric ? "5" : "15"} type="number" />

      <span style={styles.label}>EXTRA MARGIN (WET-OUT / WASTAGE)</span>
      <SelectDropdown options={EXTRA_OPTIONS} value={extra} onChange={setExtra} />

      <button style={styles.calcBtn(C.green)} onClick={calculate}>CALCULATE</button>
      <button style={styles.calcBtn(C.red)} onClick={reset}>
        <RotateCcw size={16} /> RESET
      </button>
    </div>
  );
}

function CureScreen() {
  const [method, setMethod] = useState("AMBIENT");
  const [temp, setTemp] = useState("20");
  const [result, setResult] = useState(null);
  const METHODS = ["AMBIENT", "HOT WATER", "STEAM"];

  function calculate() {
    const t = parseFloat(temp) || 20;
    let hours;
    if (method === "AMBIENT")        hours = Math.max(1, Math.round(48 / (t / 10)));
    else if (method === "HOT WATER") hours = Math.max(0.5, Math.round(24 / (t / 20)));
    else                             hours = Math.max(0.25, Math.round(8 / (t / 60)));
    setResult({ hours, method, temp: t });
  }

  return (
    <div style={styles.body}>
      <SectionPhoto
        src={IMG.backwallLevi}
        url={IMG.backwallLevi}
        maxHeight={220}
        style={{ marginBottom: 20 }}
      />
      <div style={styles.cureTitle}>
        <Clock size={28} color={C.cyan} style={{ filter: `drop-shadow(0 0 6px ${C.cyan})` }} />
        <span>CURE TIMER</span>
      </div>

      <span style={styles.label}>CURING METHOD</span>
      <div style={styles.toggleRow}>
        {METHODS.map((m) => (
          <button key={m} style={{ ...styles.toggleBtn(method === m, C.cyan), fontSize: 11 }} onClick={() => { setMethod(m); setResult(null); }}>
            {method === m && <Check size={12} />}{m}
          </button>
        ))}
      </div>

      <span style={styles.label}>TEMPERATURE (°C)</span>
      <input style={styles.input} value={temp} onChange={(e) => setTemp(e.target.value)} type="number" />

      <button style={styles.calcBtn(C.cyan)} onClick={calculate}>CALCULATE TIME</button>

      {result && (
        <div style={styles.cureResult}>
          <div style={{ color: C.cyan, fontSize: 12, letterSpacing: 3, marginBottom: 8 }}>ESTIMATED CURE TIME</div>
          <div style={{ fontSize: 48, fontWeight: 900, color: C.cyan }}>{result.hours}h</div>
          <div style={{ color: C.muted, fontSize: 12, marginTop: 4 }}>{result.method} @ {result.temp}°C</div>
        </div>
      )}

      <div style={styles.versionText}>VERSION 1.3.0</div>
    </div>
  );
}

function DataScreen() {
  return (
    <div style={styles.body}>
      <div style={styles.sectionTitle}>TECHNICAL DATA</div>
      <div style={styles.sectionSub}>:: OFFICIAL DOCUMENTATION</div>
      <div style={styles.divider} />
      {DATASHEETS.map(({ name, file }) => (
        <div key={name} style={styles.listItem} onClick={() => window.open(file, "_blank")}>
          <div style={styles.listIcon}><FileText size={24} color={C.pink} /></div>
          <div style={styles.listText}>
            <div style={styles.listTitle}>{name}</div>
            <div style={styles.listSub}>OPEN PDF</div>
          </div>
          <ChevronRight size={18} color={C.muted} />
        </div>
      ))}
    </div>
  );
}

function CertsScreen() {
  return (
    <div style={styles.body}>
      <div style={styles.sectionTitle}>CERTIFICATES</div>
      <div style={styles.sectionSub}>:: OFFICIAL APPROVALS</div>
      <div style={styles.divider} />

      {/* ISO 9001 — actual certificate, opens the PDF */}
      <div style={styles.listItem} onClick={() => window.open("/certificates/iso-9001.pdf", "_blank")}>
        <div style={{ ...styles.listIcon, background: "#fff", padding: 8 }}>
          <img src="/certificates/logos/iso.jpeg" alt="ISO 9001" style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }} />
        </div>
        <div style={styles.listText}>
          <div style={styles.listTitle}>ISO 9001:2015</div>
          <div style={styles.listSub}>OPEN CERTIFICATE · PDF</div>
        </div>
        <ChevronRight size={18} color={C.muted} />
      </div>

      {/* Other certifying / testing bodies — logos only */}
      <span style={{ ...styles.label, marginTop: 28 }}>CERTIFIED &amp; TESTED BY</span>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {CERT_BODIES.map((c) => (
          <div key={c.name} style={{ background: "#fff", borderRadius: 8, padding: "20px 16px", display: "flex", alignItems: "center", justifyContent: "center", minHeight: 92 }}>
            <img src={c.src} alt={c.name} style={{ maxWidth: "100%", maxHeight: 56, objectFit: "contain", display: "block" }} />
          </div>
        ))}
      </div>

      <div style={styles.versionText}>VERSION 1.3.0</div>
    </div>
  );
}

const SITE_PHOTOS = [
  { url: "https://www.lateralrepairs.com/uploads/_CGSmartImage/img-2121_1110-343801ea0c5e6465ba6acc35581b9b0b.jpg",    label: "Manufacturing" },
  { url: "https://www.lateralrepairs.com/uploads/_CGSmartImage/img-1911_4388-83b659b53b8e5f9c62d5e77f672189d1.jpg",   label: "Production" },
  { url: "https://www.lateralrepairs.com/uploads/_CGSmartImage/nanotech-2_1445-d2712b21d3cc525b56d5db034a69bc77.jpg", label: "MULTIline PRO" },
  { url: "https://www.lateralrepairs.com/uploads/_CGSmartImage/img-1950-1_2332-594cc86c23d98a1ce32938e716ca43b7.jpg", label: "Installation" },
  { url: "https://www.lateralrepairs.com/uploads/_CGSmartImage/img-1756-1_1070-a621643b6ca80940d166618ffde729e1.jpg", label: "Workshop" },
  { url: "https://www.lateralrepairs.com/uploads/_CGSmartImage/img-1290_6534-801eee21cf7669c38b222f7fd2775653.jpg",   label: "Process" },
];

function MediaScreen() {
  const [lightbox, setLightbox] = useState(null);
  return (
    <div style={styles.body}>
      <div style={styles.sectionTitle}>MEDIA GALLERY</div>
      <div style={styles.sectionSub}>:: SITE PHOTOS &amp; DETAILS</div>
      <div style={styles.divider} />

      {/* Photo grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 24 }}>
        {SITE_PHOTOS.map((p, i) => (
          <div
            key={i}
            onClick={() => setLightbox(p)}
            style={{ borderRadius: 6, overflow: "hidden", cursor: "pointer", aspectRatio: "4/3", background: "#1a1a1a" }}
          >
            <img
              src={p.url}
              alt={p.label}
              style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
            />
          </div>
        ))}
      </div>

      {/* Lightbox */}
      {lightbox && (
        <div
          onClick={() => setLightbox(null)}
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.92)", zIndex: 200, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 16 }}
        >
          <img src={lightbox.url} alt={lightbox.label} style={{ maxWidth: "100%", maxHeight: "80vh", borderRadius: 8, objectFit: "contain" }} />
          <div style={{ color: "#fff", marginTop: 12, fontSize: 13, letterSpacing: 2, opacity: 0.7 }}>{lightbox.label.toUpperCase()}</div>
          <div style={{ color: C.muted, marginTop: 6, fontSize: 11, letterSpacing: 1 }}>TAP TO CLOSE</div>
        </div>
      )}

      {MEDIA_ITEMS.map((item) => (
        <div key={item.name} style={styles.listItem} onClick={() => item.url && window.open(item.url, "_blank")}>
          <div style={styles.listIcon}>
            {item.isVideo ? <Video size={24} color={item.color} /> : <Image size={24} color={item.color} />}
          </div>
          <div style={styles.listText}>
            <div style={styles.listTitle}>{item.name.length > 28 ? item.name.slice(0, 28) + "…" : item.name}</div>
            <div style={styles.listSub}>{item.type}</div>
          </div>
          <ChevronRight size={18} color={C.muted} />
        </div>
      ))}
    </div>
  );
}

function ContactScreen() {
  return (
    <div style={styles.body}>
      <SectionPhoto
        src={IMG.backwall425}
        url={IMG.backwall425}
        maxHeight={160}
        style={{ marginBottom: 20 }}
      />
      <div style={styles.contactCard}>
        <div style={styles.phoneCircle}><Phone size={36} color={C.green} /></div>
        <div style={styles.contactTitle}>SUPPORT</div>
        <div style={styles.contactSub}>NYHOLM SOLUTIONS OY AB</div>

        <a href="tel:+37069876581" style={{ textDecoration: "none", color: "inherit" }}>
          <div style={styles.contactRow}>
            <Phone size={20} color={C.green} />
            <div>
              <div style={styles.contactRowLabel}>PHONE</div>
              <div style={styles.contactRowValue}>+370 698 76581</div>
            </div>
            <ChevronRight size={18} color={C.muted} style={{ marginLeft: "auto" }} />
          </div>
        </a>

        <a href="mailto:info@lateralrepairs.com" style={{ textDecoration: "none", color: "inherit" }}>
          <div style={styles.contactRow}>
            <Mail size={20} color={C.pink} />
            <div>
              <div style={styles.contactRowLabel}>EMAIL</div>
              <div style={{ ...styles.contactRowValue, fontSize: 14 }}>info@lateralrepairs.com</div>
            </div>
            <ChevronRight size={18} color={C.muted} style={{ marginLeft: "auto" }} />
          </div>
        </a>

        <div style={styles.contactRow}>
          <MapPin size={20} color={C.muted} />
          <div>
            <div style={styles.contactRowLabel}>OFFICE</div>
            <div style={styles.contactRowValue}>Paberžių g. 5, Tauragė<br />Lithuania</div>
          </div>
        </div>

        <button style={styles.visitBtn} onClick={() => window.open("https://www.lateralrepairs.com/", "_blank")}>
          <Globe size={18} color="#000" />
          VISIT WEBSITE
        </button>
      </div>
    </div>
  );
}

// ─── APP ─────────────────────────────────────────────────────────────────────
const SCREENS = {
  home:    { title: null,           component: HomeScreen },
  calc:    { title: "CALCULATOR",   component: CalcScreen },
  cure:    { title: "CURE TIME",    component: CureScreen },
  data:    { title: "DATASHEETS",   component: DataScreen },
  certs:   { title: "CERTIFICATES", component: CertsScreen },
  media:   { title: "MEDIA",        component: MediaScreen },
  contact: { title: "CONTACT",      component: ContactScreen },
};

export default function App() {
  const [screen, setScreen] = useState("home");
  const current = SCREENS[screen];
  const Component = current.component;


  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0a0a0a; }
        input[type=number]::-webkit-inner-spin-button { -webkit-appearance: none; }
        ::-webkit-scrollbar { width: 4px; background: #111; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
      `}</style>
      <div style={styles.app}>
        {/* Header */}
        <div style={styles.header}>
          {screen !== "home" ? (
            <>
              <button style={styles.backBtn} onClick={() => setScreen("home")}>
                <ChevronLeft size={26} color={C.muted} />
              </button>
              <span style={styles.pageTitle}>{current.title}</span>
            </>
          ) : (
            <>
              <div style={styles.headerLogoWrap}>
                <img src={IMG.logo} alt="Lateral Repairs" style={{ maxHeight: 44, display: "block" }} />
              </div>
              <div style={styles.headerTitle}>
                <div style={styles.brandName}>LATERAL REPAIRS</div>
                <div style={styles.brandSub}>MANUFACTURING PERFECTION</div>
              </div>
            </>
          )}
        </div>

        {/* Content */}
        <div style={{ overflowY: "auto", maxHeight: "calc(100vh - 73px)" }}>
          <Component navigate={setScreen} />
        </div>
      </div>
    </>
  );
}
