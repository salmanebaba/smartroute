import { fillMeta } from '../api'
import { Badge } from '../ui'
import styles from './BinList.module.css'

export default function BinList({ bins }) {
  if (!bins) return <div className={styles.loading}>Loading bins…</div>
  return (
    <div className={styles.list}>
      {[...bins].sort((a,b)=>b.fill_level-a.fill_level).map((bin,idx)=>{
        const meta=fillMeta(bin.fill_level)
        return (
          <div key={bin.id} className={styles.row} style={{animationDelay:`${idx*30}ms`}}>
            <span className={styles.id}>{bin.id}</span>
            <div className={styles.barWrap}><div className={styles.bar} style={{width:`${bin.fill_level}%`,background:meta.color}}/></div>
            <span className={styles.pct} style={{color:meta.color}}>{bin.fill_level}%</span>
            <Badge label={meta.label} color={meta.color} bg={meta.bg}/>
          </div>
        )
      })}
    </div>
  )
}
