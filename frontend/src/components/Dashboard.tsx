import React, { useEffect, useState } from 'react'
import { useScanner } from '../hooks/useScanner'
import { useLocalScanner } from '../hooks/useLocalScanner'
import { useStats } from '../hooks/useStats'
import { useLocalStats } from '../hooks/useLocalStats'
import { getScanHistory } from '../services/api'
import URLScanner from './URLScanner'
import ScanResultComponent from './ScanResult'
import RecentScans from './RecentScans'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import type { ScanResult } from '../types'

const STATIC_MODE = import.meta.env.VITE_STATIC_MODE === 'true'
const STAT_COLORS = ['#3b82f6', '#ef4444', '#22c55e', '#a855f7']
const Dashboard: React.FC = () => {
  const remote = useScanner()
  const local = useLocalScanner()
  const { result, loading, scan } = STATIC_MODE ? local : remote
  const remoteStats = useStats(30000)
  const localStats = useLocalStats()
  const { stats } = STATIC_MODE ? localStats : remoteStats
  const [history, setHistory] = useState<ScanResult[]>([])

  useEffect(() => {
    if (STATIC_MODE) {
      try {
        const raw = localStorage.getItem('scan_history')
        const items = raw ? JSON.parse(raw) : []
        setHistory(items.slice(0, 10))
      } catch { /* ignore */ }
    } else {
      getScanHistory(0, 10)
        .then(setHistory)
        .catch(() => {})
    }
  }, [result])

  const statCards = [
    { label: 'Total Scans', value: stats?.total_scans ?? 0, color: STAT_COLORS[0] },
    { label: 'Phishing Detected', value: stats?.phishing_count ?? 0, color: STAT_COLORS[1] },
    { label: 'Clean URLs', value: stats?.clean_count ?? 0, color: STAT_COLORS[2] },
    {
      label: 'Avg Confidence',
      value: stats ? `${(stats.avg_confidence * 100).toFixed(1)}%` : '—',
      color: STAT_COLORS[3],
    },
  ]

  const riskData = [
    { name: 'Phishing', value: stats?.phishing_count ?? 0 },
    { name: 'Clean', value: stats?.clean_count ?? 0 },
  ]

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-white">Dashboard</h2>

      {/* Stat cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <div key={card.label} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-gray-400 text-sm">{card.label}</p>
            <p className="text-3xl font-black mt-1" style={{ color: card.color }}>
              {card.value}
            </p>
          </div>
        ))}
      </div>

      {/* URL Scanner */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 space-y-4">
        <h3 className="text-lg font-semibold text-white">Scan a URL</h3>
        <URLScanner onScan={scan} loading={loading} />
        {result && <ScanResultComponent result={result} />}
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Recent scans */}
        <div className="xl:col-span-2 bg-gray-900 rounded-xl p-6 border border-gray-800">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Scans</h3>
          <RecentScans scans={history} />
        </div>

        {/* Risk distribution */}
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Distribution</h3>
          {(stats?.total_scans ?? 0) > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                  {riskData.map((_, i) => (
                    <Cell key={i} fill={i === 0 ? '#ef4444' : '#22c55e'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1f2937', border: 'none', color: '#fff' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-sm">No data yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
