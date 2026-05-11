import { useState, useEffect, useCallback } from 'react'
import { fetchSimulatedRoute, BASE_URL } from '../api'
import { Card, CardHead, StatCard, Spinner } from '../ui'
import RouteStops from './RouteStops'
import styles from './SimulationView.module.css'

export default function SimulationView() {
  // Default target date: Tomorrow at 8:00 AM
  const getDefaultTime = () => {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    d.setHours(8, 0, 0, 0)
    // Slice ensures it perfectly matches the datetime-local input format
    return d.toISOString().slice(0, 16)
  }

  const [targetDate, setTargetDate] = useState(getDefaultTime())
  const [simulation, setSimulation] = useState(null)
  const [loading, setLoading] = useState(false)

  const runSimulation = useCallback(async () => {
    setLoading(true)
    // Convert local input time back to standard ISO for the Python backend
    const isoDate = new Date(targetDate).toISOString()
    const data = await fetchSimulatedRoute(isoDate)
    setSimulation(data)
    setLoading(false)
  }, [targetDate])

  useEffect(() => {
    runSimulation()
  }, [runSimulation])

  const route = simulation?.route
  // Construct the direct iframe URL for the Folium map
  const mapSrc = `${BASE_URL}/map/simulate?target_date=${encodeURIComponent(new Date(targetDate).toISOString())}`

  return (
    <div className={styles.layout}>
      {/* ── Top Controls & Stats ── */}
      <div className={styles.topSection}>
        <Card style={{ flex: 1, padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <h2 className={styles.title}>Predictive Route Simulator</h2>
            <p className={styles.subtitle}>Select a future date. The AI will forecast bin fill levels and generate an optimized cost-saving route.</p>
          </div>
          
          <div className={styles.inputGroup}>
            <input 
              type="datetime-local" 
              className={styles.datePicker}
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
            />
            <button className={styles.refreshBtn} onClick={runSimulation} disabled={loading}>
              {loading ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>
        </Card>

        <div className={styles.kpiGrid}>
          <StatCard 
            label="Est. Route Distance" 
            value={route ? `${route.total_distance} km` : '—'} 
            accent="var(--teal)"
            sub="Impacts fuel cost" 
          />
          <StatCard 
            label="Est. Collection Time" 
            value={route ? `${route.estimated_time} min` : '—'} 
            sub="Impacts labor cost" 
          />
          <StatCard 
            label="Bins to Collect" 
            value={route?.stops?.length || 0} 
            accent="var(--amber)"
            sub="Predicted ≥ 70% full" 
          />
        </div>
      </div>

      {/* ── Bottom Split: Route List & Map ── */}
      <div className={styles.twoCol}>
        <Card style={{ display: 'flex', flexDirection: 'column' }}>
          <CardHead 
            title="Predicted Urgent Route" 
            right={route && !loading ? <span className={styles.meta}>{route.total_distance} km</span> : null}
          />
          <div className={styles.listWrap}>
            {!loading && simulation?.message ? (
              <div className={styles.empty}>{simulation.message}</div>
            ) : (
              <RouteStops route={route} loading={loading} />
            )}
          </div>
        </Card>

        <Card style={{ display: 'flex', flexDirection: 'column' }}>
          <CardHead title="Future Simulation Map" />
          <div className={styles.mapWrap}>
             {loading ? (
               <div className={styles.mapLoading}><Spinner/> Generating AI map...</div>
             ) : (
               <iframe key={mapSrc} src={mapSrc} className={styles.frame} title="Simulated Map" allowFullScreen/>
             )}
          </div>
        </Card>
      </div>
    </div>
  )
}