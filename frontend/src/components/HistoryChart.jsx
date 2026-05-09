import { ComposedChart, Area, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import styles from './HistoryChart.module.css'

const Tip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className={styles.tooltip}>
      <div className={styles.ttDay}>{label}</div>
      {payload.map(p => (
        <div key={p.dataKey} className={styles.ttRow} style={{ color: p.color }}>
          <span>{p.name}</span>
          <span className={styles.ttVal}>
            {p.value}{p.dataKey === 'avgFill' ? '%' : ''}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function HistoryChart({ data }) {
  if (!data) return <div className={styles.empty}>Loading history…</div>
  return (
    <div className={styles.wrap}>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -16 }}>
          <defs>
            <linearGradient id="fillGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2fffa0" stopOpacity={0.18} />
              <stop offset="95%" stopColor="#2fffa0" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
          {/* Changed dataKey to "date" */}
          <XAxis dataKey="date" tick={{ fill: '#4d574e', fontSize: 11, fontFamily: 'DM Mono' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#4d574e', fontSize: 11, fontFamily: 'DM Mono' }} axisLine={false} tickLine={false} />
          <Tooltip content={<Tip />} />
          <Legend wrapperStyle={{ fontSize: 11, color: '#8a968b', paddingTop: 8, fontFamily: 'DM Mono' }} iconSize={8} />
          
          {/* Updated dataKeys here! */}
          <Area type="monotone" dataKey="avgFill" name="Avg fill %" stroke="#2fffa0" strokeWidth={1.5} fill="url(#fillGrad)" dot={{ r: 3, fill: '#2fffa0', strokeWidth: 0 }} activeDot={{ r: 5, fill: '#2fffa0' }} />
          <Bar dataKey="collected" name="Bins collected" fill="rgba(92,158,255,0.35)" radius={[3, 3, 0, 0]} maxBarSize={24} />
          <Bar dataKey="urgent" name="Urgent bins" fill="rgba(255,92,92,0.35)" radius={[3, 3, 0, 0]} maxBarSize={24} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}