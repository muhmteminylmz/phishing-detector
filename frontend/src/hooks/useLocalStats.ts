import { useState, useEffect, useCallback } from 'react'
import type { StatsResponse } from '../types'

interface UseLocalStatsReturn {
  stats: StatsResponse | null
  loading: boolean
  refresh: () => void
}

interface StoredScan {
  is_phishing: boolean
  confidence: number
}

export function useLocalStats(): UseLocalStatsReturn {
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(() => {
    try {
      const raw = localStorage.getItem('scan_history')
      const history: StoredScan[] = raw ? JSON.parse(raw) : []
      const total = history.length
      const phishing = history.filter(s => s.is_phishing).length
      const clean = total - phishing
      const avgConf = total > 0
        ? history.reduce((acc, s) => acc + s.confidence, 0) / total
        : 0
      setStats({
        total_scans: total,
        phishing_count: phishing,
        clean_count: clean,
        avg_confidence: Math.round(avgConf * 10000) / 10000,
        phishing_rate: total > 0 ? Math.round((phishing / total) * 10000) / 10000 : 0,
      })
    } catch {
      setStats({ total_scans: 0, phishing_count: 0, clean_count: 0, avg_confidence: 0, phishing_rate: 0 })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  return { stats, loading, refresh }
}
