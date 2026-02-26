import { useState, useCallback } from 'react'
import { scanUrlLocally, type LocalScanResult } from '../services/phishingEngine'
import toast from 'react-hot-toast'

const MAX_HISTORY = 200

interface UseLocalScannerReturn {
  result: LocalScanResult | null
  loading: boolean
  error: string | null
  scan: (url: string) => Promise<void>
  reset: () => void
}

export function useLocalScanner(): UseLocalScannerReturn {
  const [result, setResult] = useState<LocalScanResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const scan = useCallback(async (url: string) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await scanUrlLocally(url)
      setResult(data)

      // Persist to localStorage for history / stats
      try {
        const history: LocalScanResult[] = JSON.parse(localStorage.getItem('scan_history') ?? '[]')
        history.unshift(data)
        // Keep last 200 scans
        localStorage.setItem('scan_history', JSON.stringify(history.slice(0, MAX_HISTORY)))
      } catch { /* storage full – ignore */ }

      if (data.is_phishing) {
        toast.error(`⚠️ Phishing detected! Risk: ${data.risk_level}`)
      } else {
        toast.success(`✅ URL appears safe (${data.risk_level} risk)`)
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Scan failed'
      setError(msg)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setResult(null)
    setError(null)
  }, [])

  return { result, loading, error, scan, reset }
}
