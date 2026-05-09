import { fillMeta } from '../api'
import { Badge, Spinner } from '../ui'
import styles from './RouteStops.module.css'

export default function RouteStops({ route, loading }) {
  if (loading) return <div className={styles.loading}><Spinner/> Optimising…</div>
  if (!route) return <div className={styles.loading}>No route data</div>
  return (
    <div className={styles.list}>
      {route.stops.map((stop,idx)=>{
        const meta=fillMeta(stop.bin.fill_level)
        return (
          <div key={stop.bin.id} className={styles.row} style={{animationDelay:`${idx*35}ms`}}>
            <div className={styles.num}>{stop.order}</div>
            <div className={styles.info}>
              <span className={styles.binId}>{stop.bin.id}</span>
              <span className={styles.detail}>{stop.bin.fill_level}% full · <span className={styles.dist}>+{stop.distance_from_previous} km</span></span>
            </div>
            <Badge label={meta.label} color={meta.color} bg={meta.bg}/>
          </div>
        )
      })}
    </div>
  )
}
