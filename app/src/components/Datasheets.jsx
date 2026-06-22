import { useEffect, useState } from 'react'
import { FileText, ArrowLeft } from 'lucide-react'
import { DATASHEETS } from '../data/resins.js'

// Resolve a public-folder path against Vite's base URL.
const asset = (p) => `${import.meta.env.BASE_URL}${p}`.replace(/\/{2,}/g, '/')

export default function Datasheets() {
  const [open, setOpen] = useState(null) // datasheet being viewed
  const [available, setAvailable] = useState({}) // id -> bool (file exists?)

  // Probe which datasheet PDFs are actually present in /public/datasheets.
  useEffect(() => {
    let cancelled = false
    Promise.all(
      DATASHEETS.map(async (d) => {
        if (!d.file) return [d.id, false]
        try {
          const res = await fetch(asset(d.file), { method: 'HEAD' })
          const ok = res.ok && (res.headers.get('content-type') || '').includes('pdf')
          return [d.id, ok]
        } catch {
          return [d.id, false]
        }
      }),
    ).then((pairs) => {
      if (!cancelled) setAvailable(Object.fromEntries(pairs))
    })
    return () => { cancelled = true }
  }, [])

  if (open) {
    return (
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: 14, borderBottom: '1px solid var(--line)' }}>
          <button className="ds button soon" onClick={() => setOpen(null)} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <ArrowLeft size={16} /> Back
          </button>
          <b>{open.title}</b>
        </div>
        <iframe
          title={open.title}
          src={asset(open.file)}
          style={{ width: '100%', height: '70vh', border: 0, background: '#fff' }}
        />
      </div>
    )
  }

  return (
    <div className="card">
      <h2>Technical datasheets</h2>
      {DATASHEETS.map((d) => {
        const ready = available[d.id]
        return (
          <div className="ds" key={d.id}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <FileText size={20} color="var(--cyan)" />
              <div>
                <div className="t">{d.title}</div>
                <div className="tag">{ready ? 'PDF · tap to view' : 'Coming soon'}</div>
              </div>
            </div>
            {ready ? (
              <a href="#" onClick={(e) => { e.preventDefault(); setOpen(d) }}>View</a>
            ) : (
              <button className="soon" disabled>Soon</button>
            )}
          </div>
        )
      })}
      <p className="muted small" style={{ marginTop: 14, marginBottom: 0 }}>
        Datasheet PDFs live in <code>public/datasheets/</code>. Drop the files in (matching the
        names in <code>src/data/resins.js</code>) and they appear here automatically.
      </p>
    </div>
  )
}
