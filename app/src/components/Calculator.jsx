import { useMemo, useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { RESINS, LINERS } from '../data/resins.js'
import {
  splitMix, estimateResinLitres, litresToGallons, round, ratioLabel,
  IN_TO_MM, FT_TO_M, L_TO_GAL,
} from '../lib/calc.js'

export default function Calculator() {
  const [units, setUnits] = useState('metric') // 'metric' | 'imperial'
  const [resinId, setResinId] = useState('fc15')
  const [linerId, setLinerId] = useState('drainplus')

  // raw inputs in the active unit system
  const [diameter, setDiameter] = useState('150') // mm or in
  const [length, setLength] = useState('5') // m or ft
  const [wall, setWall] = useState('3.0') // mm or in

  const resin = RESINS.find((r) => r.id === resinId)
  const liner = LINERS.find((l) => l.id === linerId)

  // keep wall in sync when a liner preset is chosen (except custom)
  function chooseLiner(id) {
    setLinerId(id)
    const l = LINERS.find((x) => x.id === id)
    if (l && l.id !== 'custom') {
      setWall(units === 'metric' ? String(l.wallMm) : String(round(l.wallMm / IN_TO_MM, 3)))
    }
  }

  const calc = useMemo(() => {
    const d = parseFloat(diameter) || 0
    const len = parseFloat(length) || 0
    const w = parseFloat(wall) || 0

    const diameterMm = units === 'metric' ? d : d * IN_TO_MM
    const lengthM = units === 'metric' ? len : len * FT_TO_M
    const wallMm = units === 'metric' ? w : w * IN_TO_MM

    const litres = estimateResinLitres({ diameterMm, lengthM, wallMm })
    const split = splitMix(litres, resin.mix)
    return { litres, split }
  }, [diameter, length, wall, units, resin])

  const isMetric = units === 'metric'
  const volUnit = isMetric ? 'L' : 'gal'
  const fmtVol = (l) => round(isMetric ? l : litresToGallons(l), 2)

  const unverified = !resin.verified || (liner && !liner.verified)

  return (
    <>
      {unverified && (
        <div className="warn">
          <AlertTriangle size={18} />
          <div>
            <b>Draft figures.</b> Some values here (liner wall thickness / saturation)
            are typical placeholders, not yet confirmed against the datasheet. The
            resin <b>mix ratio</b> is correct — verify the total volume before ordering.
          </div>
        </div>
      )}

      <div className="card">
        <h2>Resin mix calculator</h2>

        <div className="field">
          <div className="seg" role="group" aria-label="Units">
            <button className={isMetric ? 'active' : ''} onClick={() => setUnits('metric')}>Metric</button>
            <button className={!isMetric ? 'active' : ''} onClick={() => setUnits('imperial')}>Imperial</button>
          </div>
        </div>

        <div className="field">
          <label htmlFor="resin">Resin system</label>
          <select id="resin" className="input" value={resinId} onChange={(e) => setResinId(e.target.value)}>
            {RESINS.map((r) => (
              <option key={r.id} value={r.id}>{r.name} — {ratioLabel(r.mix)}</option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="liner">Liner</label>
          <select id="liner" className="input" value={linerId} onChange={(e) => chooseLiner(e.target.value)}>
            {LINERS.map((l) => (
              <option key={l.id} value={l.id}>{l.name}</option>
            ))}
          </select>
        </div>

        <div className="row2">
          <div className="field">
            <label htmlFor="dia">Diameter {isMetric ? '(mm)' : '(in)'}</label>
            <input id="dia" className="input" type="number" inputMode="decimal" value={diameter} onChange={(e) => setDiameter(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="len">Length {isMetric ? '(m)' : '(ft)'}</label>
            <input id="len" className="input" type="number" inputMode="decimal" value={length} onChange={(e) => setLength(e.target.value)} />
          </div>
        </div>

        <div className="field">
          <label htmlFor="wall">Liner wall thickness {isMetric ? '(mm)' : '(in)'}</label>
          <input id="wall" className="input" type="number" inputMode="decimal" value={wall} onChange={(e) => { setWall(e.target.value); setLinerId('custom') }} />
        </div>
      </div>

      <div className="card">
        <h2>Result <span className="ratio-badge">{resin.short} · {ratioLabel(resin.mix)}</span></h2>

        <div className="result total">
          <span className="k">Total resin needed</span>
          <span className="v">{fmtVol(calc.litres)} <span className="sub">{volUnit}</span></span>
        </div>

        {resin.singleComponent ? (
          <div className="result">
            <span className="k">{resin.short} (single component)</span>
            <span className="v">{fmtVol(calc.litres)} <span className="sub">{volUnit}</span></span>
          </div>
        ) : (
          <>
            <div className="result">
              <span className="k">Resin (part A)</span>
              <span className="v">{fmtVol(calc.split.resin)} <span className="sub">{volUnit}</span></span>
            </div>
            <div className="result">
              <span className="k">Hardener (part B)</span>
              <span className="v">{fmtVol(calc.split.hardener)} <span className="sub">{volUnit}</span></span>
            </div>
          </>
        )}

        <p className="muted small" style={{ marginTop: 14, marginBottom: 0 }}>
          Mix ratio {ratioLabel(resin.mix)} by weight. Pot life {resin.potLife}. Volume is an
          estimate from liner geometry (π · D · L · t); always confirm against the datasheet and
          allow for wastage.
        </p>
      </div>
    </>
  )
}
