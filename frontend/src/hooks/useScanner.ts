import { useState, useCallback } from 'react'
import { scanUrl } from '../services/api'
import type { ScanResult } from '../types'
import toast from 'react-hot-toast'

interface UseScannerReturn {
  result: ScanResult | null
  loading: boolean
  error: string | null
  scan: (url: string) => Promise<void>
  reset: () => void
}

export function useScanner(): UseScannerReturn {
  const [result, setResult] = useState<ScanResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const scan = useCallback(async (url: string) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await scanUrl(url)
      setResult(data)
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
