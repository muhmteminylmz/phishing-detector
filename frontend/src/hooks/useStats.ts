import { useState, useEffect, useCallback } from 'react'
import { getStats } from '../services/api'
import type { StatsResponse } from '../types'

interface UseStatsReturn {
  stats: StatsResponse | null
  loading: boolean
  refresh: () => void
}

export function useStats(pollInterval = 30000): UseStatsReturn {
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    try {
      const data = await getStats()
      setStats(data)
    } catch {
      // silently ignore stats errors
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, pollInterval)
    return () => clearInterval(interval)
  }, [refresh, pollInterval])

  return { stats, loading, refresh }
}
