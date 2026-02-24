import React from 'react'
import { clsx } from 'clsx'
import type { ScanResult } from '../types'

interface Props {
  scans: ScanResult[]
}

const BADGE: Record<string, string> = {
  LOW: 'bg-green-700 text-green-100',
  MEDIUM: 'bg-yellow-700 text-yellow-100',
  HIGH: 'bg-orange-700 text-orange-100',
  CRITICAL: 'bg-red-700 text-red-100',
}

const RecentScans: React.FC<Props> = ({ scans }) => {
  if (scans.length === 0) {
    return <p className="text-gray-500 text-sm">No scans yet.</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-gray-400 border-b border-gray-800">
            <th className="text-left py-2 pr-4">URL</th>
            <th className="text-left py-2 pr-4">Risk</th>
            <th className="text-left py-2 pr-4">Score</th>
            <th className="text-left py-2">Time</th>
          </tr>
        </thead>
        <tbody>
          {scans.map((s) => (
            <tr key={s.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
              <td className="py-2 pr-4 max-w-xs truncate text-gray-300">
                {s.url}
              </td>
              <td className="py-2 pr-4">
                <span className={clsx('px-2 py-0.5 rounded text-xs font-semibold', BADGE[s.risk_level])}>
                  {s.risk_level}
                </span>
              </td>
              <td className="py-2 pr-4 text-gray-300">{s.risk_score}</td>
              <td className="py-2 text-gray-500 text-xs">
                {new Date(s.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default RecentScans
