import { useState, useEffect } from 'react'
import { apiFetch } from './api'
import ManagerView from './components/ManagerView'
import DriverView  from './components/DriverView'
import SimulationView from './components/SimulationView' // <-- Import the new view
import styles from './App.module.css'

export default function App() {
  // Add 'simulation' to your view state logic
  const [view, setView]     = useState('manager') 
  const [online, setOnline] = useState(null)

  useEffect(() => {
    apiFetch('/health').then(d => setOnline(!!d))
    const id = setInterval(() => apiFetch('/health').then(d => setOnline(!!d)), 15000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className={styles.root}>
      <nav className={styles.nav}>
        <div className={styles.logo}>
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <rect x="1" y="1" width="7" height="7" rx="2" fill="var(--teal)" opacity="0.9"/>
            <rect x="10" y="1" width="7" height="7" rx="2" fill="var(--teal)" opacity="0.5"/>
            <rect x="1" y="10" width="7" height="7" rx="2" fill="var(--teal)" opacity="0.5"/>
            <rect x="10" y="10" width="7" height="7" rx="2" fill="var(--teal)" opacity="0.25"/>
          </svg>
          <span>SmartRoute</span>
        </div>
        <div className={styles.tabs}>
          <button className={`${styles.tab} ${view==='manager'?styles.tabActive:''}`} onClick={()=>setView('manager')}>Manager</button>
          <button className={`${styles.tab} ${view==='driver'?styles.tabActive:''}`} onClick={()=>setView('driver')}>Driver</button>
          {/* ── New Simulator Tab ── */}
          <button className={`${styles.tab} ${view==='simulation'?styles.tabActive:''}`} onClick={()=>setView('simulation')}>AI Simulator</button>
        </div>
        <div className={styles.status}>
          <div className={`${styles.dot} ${online===null?styles.dotChecking:online?styles.dotOnline:styles.dotOffline}`}/>
          <span className={styles.statusText}>{online===null?'Connecting…':online?'API online':'Mock data'}</span>
        </div>
      </nav>
      <main>
        {/* Render the correct view */}
        {view === 'manager' && <ManagerView />}
        {view === 'driver' && <DriverView />}
        {view === 'simulation' && <SimulationView />}
      </main>
    </div>
  )
}