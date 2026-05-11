import { useState, useEffect, useCallback } from 'react'
// Import the dedicated fetchers we built
import { fetchStats, fetchBins, fetchOptimizedRoute, fetchHistory } from '../api'
import { Card, CardHead, StatCard, StrategyPicker } from '../ui'
import BinList from './BinList'
import RouteStops from './RouteStops'
import HistoryChart from './HistoryChart'
import MapFrame from './MapFrame'
import styles from './ManagerView.module.css'

const STRATEGIES = [
  { value: 'distance', label: 'Distance' },
  { value: 'fill_level', label: 'Fill level' },
  { value: 'time', label: 'Time' },
]

export default function ManagerView() {
  const [stats, setStats] = useState(null)
  const [bins, setBins] = useState(null)
  const [route, setRoute] = useState(null)
  const [history, setHistory] = useState(null)
  const [strategy, setStrategy] = useState('distance')
  const [routeLoading, setRouteLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [mapDebug, setMapDebug] = useState(false)

  const loadData = useCallback(async () => {
    // Cleaner API calls!
    const [s, b] = await Promise.all([fetchStats(), fetchBins()])
    setStats(s)
    setBins(b)
    setLastUpdated(new Date().toLocaleTimeString())
  }, [])

  const loadHistory = useCallback(async () => {
    const h = await fetchHistory('7d')
    setHistory(h)
  }, [])

  const loadRoute = useCallback(async (s) => {
    setRouteLoading(true)
    const r = await fetchOptimizedRoute(s)
    setRoute(r)
    setRouteLoading(false)
  }, [])

  useEffect(() => {
    loadData()
    loadHistory()
    loadRoute('distance')
    
    // Auto-refresh every 30 seconds
    const id = setInterval(loadData, 30000)
    return () => clearInterval(id)
  }, [loadData, loadHistory, loadRoute])

  function handleStrategy(s) { 
    setStrategy(s)
    loadRoute(s) 
  }

  // Calculate urgent bins from live telemetry
  const urgentCount = bins ? bins.filter(b => b.fill_level >= 85).length : null

  return (
    <div className={styles.layout}>
      {/* ── KPI ROW ── */}
      <div className={styles.kpiRow}>
        <StatCard label="Total bins" value={stats?.total_bins} sub="registered"/>
        <StatCard label="Need collection" value={stats?.bins_needing_collection} accent="var(--amber)" sub="above threshold"/>
        <StatCard label="Avg fill level" value={stats ? `${stats.average_fill_level.toFixed(1)}%` : null} sub="fleet average"/>
        <StatCard 
          label="Urgency rate" 
          value={stats ? `${stats.collection_percentage.toFixed(0)}%` : null} 
          accent={stats && stats.collection_percentage > 70 ? 'var(--red)' : stats && stats.collection_percentage > 40 ? 'var(--amber)' : 'var(--teal)'} 
          sub="bins ready"
        />
        <StatCard label="Urgent now" value={urgentCount ?? '—'} accent="var(--red)" sub="≥85% full"/>
      </div>

      {/* ── MIDDLE ROW ── */}
      <div className={styles.twoCol}>
        <Card>
          <CardHead title="Bin fill levels" right={<span className={styles.meta}>{bins ? `${bins.length} bins` : ''}{lastUpdated && ` · ${lastUpdated}`}</span>}/>
          <BinList bins={bins}/>
        </Card>
        <Card>
          <CardHead title="Optimised route" right={route && !routeLoading ? <span className={styles.meta}>{route.total_distance} km · {route.estimated_time} min</span> : null}/>
          <div className={styles.stratWrap}>
            <StrategyPicker value={strategy} onChange={handleStrategy} options={STRATEGIES}/>
          </div>
          <RouteStops route={route} loading={routeLoading}/>
        </Card>
      </div>

      {/* ── BOTTOM ROW ── */}
      <div className={styles.twoCol}>
        <Card>
          <CardHead title="7-day history" right={<button className={styles.refreshBtn} onClick={loadHistory}>Refresh</button>}/>
          <HistoryChart data={history}/>
        </Card>
        <Card style={{ display: 'flex', flexDirection: 'column' }}>
          <CardHead title="Map view" right={
            <div className={styles.mapToggleRow}>
              <button className={`${styles.mapToggle} ${!mapDebug ? styles.mapToggleActive : ''}`} onClick={() => setMapDebug(false)}>Route</button>
              <button className={`${styles.mapToggle} ${mapDebug ? styles.mapToggleActive : ''}`} onClick={() => setMapDebug(true)}>All bins</button>
            </div>
          }/>
          <MapFrame strategy={strategy} debug={mapDebug} height={280}/>
        </Card>
      </div>
    </div>
  )
}