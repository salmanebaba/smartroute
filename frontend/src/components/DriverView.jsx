import { useState, useEffect, useCallback } from 'react'
// Import the dedicated fetcher we built instead of raw apiFetch
import { fetchOptimizedRoute, fillMeta } from '../api' 
import { Card, CardHead, StatCard, StrategyPicker, Badge } from '../ui'
import MapFrame from './MapFrame'
import styles from './DriverView.module.css'

const STRATEGIES = [
  { value: 'distance',   label: 'Distance' },
  { value: 'fill_level', label: 'Fill level' },
  { value: 'time',       label: 'Time' },
]

export default function DriverView() {
  const [strategy, setStrategy] = useState('distance')
  const [route, setRoute]       = useState(null)
  const [done, setDone]         = useState(new Set())
  const [loading, setLoading]   = useState(true)

  // Cleaner async data loading
  const loadRoute = useCallback(async (s) => {
    setLoading(true)
    const data = await fetchOptimizedRoute(s)
    setRoute(data)
    setLoading(false)
  }, [])

  useEffect(() => {
    setDone(new Set()) // Reset driver progress if the route strategy changes
    loadRoute(strategy)
  }, [strategy, loadRoute])

  function handleStrategy(s) {
    setStrategy(s)
  }

  function toggle(id) {
    setDone(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const total     = route?.stops?.length ?? 0
  const completed = done.size
  const pct       = total ? Math.round((completed / total) * 100) : 0

  return (
    <div className={styles.layout}>
      {/* ── Sidebar ── */}
      <aside className={styles.sidebar}>
        {/* Progress */}
        <div className={styles.progressCard}>
          <div className={styles.progressHeader}>
            <span className={styles.progressLabel}>Route progress</span>
            <span className={styles.progressCount}>{completed}/{total}</span>
          </div>
          <div className={styles.progressTrack}>
            <div className={styles.progressFill} style={{ width: `${pct}%` }} />
          </div>
          <div className={styles.progressPct}>{pct}%</div>
        </div>

        {/* Stats row */}
        <div className={styles.statsRow}>
          <StatCard
            label="Distance"
            value={route ? `${route.total_distance} km` : '—'}
          />
          <StatCard
            label="Est. time"
            value={route ? `${route.estimated_time} min` : '—'}
          />
        </div>

        {/* Strategy */}
        <Card>
          <CardHead title="Strategy" />
          <div className={styles.stratPad}>
            <StrategyPicker
              value={strategy}
              onChange={handleStrategy}
              options={STRATEGIES}
            />
          </div>
        </Card>

        {/* Stop list */}
        <Card style={{ flex: 1, minHeight: 0 }}>
          <CardHead
            title="Stops"
            right={<span className={styles.stopCount}>{total} stops</span>}
          />
          <div className={styles.stopList}>
            {loading && (
              <div className={styles.empty}>Loading route…</div>
            )}
            {!loading && route?.stops.map((stop, idx) => {
              const meta  = fillMeta(stop.bin.fill_level)
              const isDone = done.has(stop.bin.id)
              return (
                <div
                  key={stop.bin.id}
                  className={`${styles.stopRow} ${isDone ? styles.stopDone : ''}`}
                  style={{ animationDelay: `${idx * 30}ms` }}
                >
                  <div className={`${styles.stopNum} ${isDone ? styles.numDone : ''}`}>
                    {isDone ? '✓' : stop.order}
                  </div>
                  <div className={styles.stopInfo}>
                    <span className={styles.stopId}>{stop.bin.id}</span>
                    <span className={styles.stopDetail}>
                      {stop.bin.fill_level}% · +{stop.distance_from_previous} km
                    </span>
                  </div>
                  <Badge label={meta.label} color={meta.color} bg={meta.bg} />
                  <button
                    className={`${styles.doneBtn} ${isDone ? styles.doneBtnActive : ''}`}
                    onClick={() => toggle(stop.bin.id)}
                  >
                    {isDone ? 'Undo' : 'Done'}
                  </button>
                </div>
              )
            })}
          </div>
        </Card>
      </aside>

      {/* ── Map ── */}
      <div className={styles.mapWrap}>
        <Card style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <CardHead
            title="Live route map"
            right={
              <div className={styles.mapMeta}>
                <span className={styles.liveDot} />
                <span>{strategy} strategy</span>
              </div>
            }
          />
          <MapFrame strategy={strategy} height="100%" />
        </Card>
      </div>
    </div>
  )
}