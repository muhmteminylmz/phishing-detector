import React, { useState, useEffect } from 'react'
import { getScanHistory } from '../services/api'
import type { ScanResult } from '../types'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'

const STATIC_MODE = import.meta.env.VITE_STATIC_MODE === 'true'

const Statistics: React.FC = () => {
  const [history, setHistory] = useState<ScanResult[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (STATIC_MODE) {
      try {
        const raw = localStorage.getItem('scan_history')
        setHistory(raw ? JSON.parse(raw) : [])
      } catch { /* ignore */ }
      setLoading(false)
    } else {
      getScanHistory(0, 100)
        .then(setHistory)
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [])

  // Group by date
  const byDate: Record<string, { date: string; total: number; phishing: number }> = {}
  history.forEach((s) => {
    const date = new Date(s.created_at).toLocaleDateString()
    if (!byDate[date]) byDate[date] = { date, total: 0, phishing: 0 }
    byDate[date].total += 1
    if (s.is_phishing) byDate[date].phishing += 1
  })
  const chartData = Object.values(byDate).slice(-30)

  if (loading) return <p className="p-6 text-gray-400">Loading...</p>

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-white">Statistics</h2>

      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <h3 className="text-lg font-semibold text-white mb-4">Daily Scans (Last 30 days)</h3>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af' }} />
              <Tooltip contentStyle={{ background: '#1f2937', border: 'none', color: '#fff' }} />
              <Line type="monotone" dataKey="total" stroke="#3b82f6" name="Total" dot={false} />
              <Line type="monotone" dataKey="phishing" stroke="#ef4444" name="Phishing" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-500 text-sm">No data available yet.</p>
        )}
      </div>

      {/* Summary table */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <h3 className="text-lg font-semibold text-white mb-4">Summary</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-3xl font-black text-blue-500">{history.length}</p>
            <p className="text-gray-400 text-sm mt-1">Total Scans</p>
          </div>
          <div>
            <p className="text-3xl font-black text-red-500">{history.filter(s => s.is_phishing).length}</p>
            <p className="text-gray-400 text-sm mt-1">Phishing</p>
          </div>
          <div>
            <p className="text-3xl font-black text-green-500">{history.filter(s => !s.is_phishing).length}</p>
            <p className="text-gray-400 text-sm mt-1">Clean</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Statistics
