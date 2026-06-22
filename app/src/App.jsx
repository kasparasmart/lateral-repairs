import { useState } from 'react'
import { Calculator as CalcIcon, FileText } from 'lucide-react'
import Calculator from './components/Calculator.jsx'
import Datasheets from './components/Datasheets.jsx'

export default function App() {
  const [tab, setTab] = useState('calc') // 'calc' | 'datasheets'

  return (
    <div className="app">
      <header className="header">
        <img src={`${import.meta.env.BASE_URL}logo.png`} alt="Lateral Repairs" />
        <div className="brand">
          <b>Lateral Repairs</b>
          <span>Technical toolkit</span>
        </div>
      </header>

      {tab === 'calc' ? <Calculator /> : <Datasheets />}

      <nav className="tabbar">
        <button className={tab === 'calc' ? 'active' : ''} onClick={() => setTab('calc')}>
          <CalcIcon size={22} />
          Calculator
        </button>
        <button className={tab === 'datasheets' ? 'active' : ''} onClick={() => setTab('datasheets')}>
          <FileText size={22} />
          Datasheets
        </button>
      </nav>
    </div>
  )
}
