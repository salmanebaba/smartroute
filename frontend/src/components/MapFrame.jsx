import { BASE_URL } from '../api'
import styles from './MapFrame.module.css'

export default function MapFrame({ strategy='distance', height=360, debug=false }) {
  const src = debug ? `${BASE_URL}/map/debug` : `${BASE_URL}/map?strategy=${strategy}`
  return (
    <div className={styles.wrap} style={{height}}>
      <iframe key={src} src={src} className={styles.frame} title="Route map" allowFullScreen/>
      <div className={styles.hint}>Map from <code>{debug?'/map/debug':`/map?strategy=${strategy}`}</code></div>
    </div>
  )
}
