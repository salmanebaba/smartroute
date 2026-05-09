import styles from './ui.module.css'

export function Card({ children, className='', style }) {
  return <div className={`${styles.card} ${className}`} style={style}>{children}</div>
}
export function CardHead({ title, right }) {
  return <div className={styles.cardHead}><span className={styles.cardTitle}>{title}</span>{right&&<div className={styles.cardRight}>{right}</div>}</div>
}
export function Badge({ label, color, bg }) {
  return <span className={styles.badge} style={{color,background:bg}}>{label}</span>
}
export function Spinner({ size=16 }) {
  return <span className={styles.spinner} style={{width:size,height:size}}/>
}
export function StatCard({ label, value, sub, accent }) {
  return (
    <div className={styles.statCard}>
      <div className={styles.statLabel}>{label}</div>
      <div className={styles.statValue} style={accent?{color:accent}:{}}>{value??'—'}</div>
      {sub&&<div className={styles.statSub}>{sub}</div>}
    </div>
  )
}
export function StrategyPicker({ value, onChange, options }) {
  return (
    <div className={styles.stratRow}>
      {options.map(o=>(
        <button key={o.value} className={`${styles.stratBtn} ${value===o.value?styles.stratActive:''}`} onClick={()=>onChange(o.value)}>{o.label}</button>
      ))}
    </div>
  )
}
