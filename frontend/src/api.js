export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Core fetch wrapper
export async function apiFetch(path) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, { signal: AbortSignal.timeout(4500) })
    if (!res.ok) throw new Error(res.status)
    return await res.json()
  } catch (error) { 
    console.error(`API fetch failed for ${path}:`, error)
    return null 
  }
}

// ─── API FETCH FUNCTIONS ──────────────────────────────────────────────

export async function fetchStats() {
  const data = await apiFetch('/bins/statistics')
  return data || MOCK_STATS
}

export async function fetchHistory(range = '7d') {
  const data = await apiFetch(`/bins/statistics/history?range=${range}`)
  return transformHistory(data)
}

export async function fetchOptimizedRoute(strategy = 'distance') {
  const data = await apiFetch(`/route/optimize?strategy=${strategy}`)
  return data || generateMockRoute(strategy)
}

export async function fetchBins() {
  const data = await apiFetch('/debug-data')
  // The debug-data endpoint returns { total_bins: X, bins: [...] }
  return data?.bins || MOCK_BINS
}


// ─── UTILS & FORMATTERS ───────────────────────────────────────────────

export function transformHistory(backendHistory) {
  if (!backendHistory || !backendHistory.daily_data || backendHistory.daily_data.length === 0) {
    return generateMockHistory()
  }
  
  // The backend returns it newest-first, but charts need oldest-first
  const reversedData = [...backendHistory.daily_data].reverse()

  return reversedData.map(day => {
    // Safely extract MM-DD from "YYYY-MM-DD" to avoid timezone shifts
    const dateStr = day.date.substring(5) 

    return {
      date: dateStr, // Used for the X-axis label
      avgFill: Math.round(day.average_fill_level),
      collected: day.bins_collected,
      urgent: day.urgent_count,
    }
  })
}

export function fillMeta(pct) {
  if (pct >= 85) return { label: 'Urgent', color: 'var(--red)',   bg: 'var(--red-bg)' }
  if (pct >= 50) return { label: 'Medium', color: 'var(--amber)', bg: 'var(--amber-bg)' }
  return              { label: 'Low',    color: 'var(--teal)',  bg: 'var(--teal-bg)' }
}


// ─── MOCK DATA FALLBACKS ──────────────────────────────────────────────

export const MOCK_BINS = [
  { id: 'bin_001', latitude: 33.9810, longitude: -6.8690, fill_level: 92 },
  { id: 'bin_002', latitude: 33.9790, longitude: -6.8650, fill_level: 44 },
  { id: 'bin_003', latitude: 33.9830, longitude: -6.8620, fill_level: 85 },
  { id: 'bin_004', latitude: 33.9770, longitude: -6.8700, fill_level: 28 },
  { id: 'bin_005', latitude: 33.9850, longitude: -6.8600, fill_level: 77 },
]

export const MOCK_STATS = {
  total_bins: 10, bins_needing_collection: 6,
  average_fill_level: 58.2, collection_percentage: 60.0,
}

export function generateMockHistory() {
  const days = ['05-03', '05-04', '05-05', '05-06', '05-07', '05-08', '05-09']
  return days.map((date, i) => ({
    date,
    avgFill: Math.round(40 + Math.sin(i * 0.9) * 18 + Math.random() * 8),
    collected: Math.round(3 + Math.random() * 5),
    urgent: Math.round(1 + Math.random() * 4),
  }))
}

export function generateMockRoute(strategy) {
  let bins = [...MOCK_BINS].filter(b => b.fill_level > 35)
  if (strategy === 'fill_level') bins.sort((a, b) => b.fill_level - a.fill_level)
  else if (strategy === 'time') bins.sort((a, b) => a.id.localeCompare(b.id))
  else bins.sort((a, b) => a.longitude - b.longitude)
  return {
    strategy,
    total_distance: parseFloat((bins.length * 0.6 + Math.random() * 2).toFixed(1)),
    estimated_time: Math.round(bins.length * 3.5 + Math.random() * 5),
    stops: bins.map((bin, i) => ({
      bin, order: i + 1,
      distance_from_previous: parseFloat((0.3 + Math.random() * 1.4).toFixed(2)),
    })),
  }
}

export async function fetchSimulatedRoute(isoDate) {
  const data = await apiFetch(`/ai/simulate-route?target_date=${encodeURIComponent(isoDate)}`)
  return data
}