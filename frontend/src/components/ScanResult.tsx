import React, { useState } from 'react'
import { ClipboardDocumentIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import type { ScanResult } from '../types'
import toast from 'react-hot-toast'

interface Props {
  result: ScanResult
}

const RISK_COLORS: Record<string, string> = {
  LOW: 'bg-green-900 border-green-600',
  MEDIUM: 'bg-yellow-900 border-yellow-500',
  HIGH: 'bg-orange-900 border-orange-500',
  CRITICAL: 'bg-red-900 border-red-600',
}

const RISK_BADGE: Record<string, string> = {
  LOW: 'bg-green-600',
  MEDIUM: 'bg-yellow-500',
  HIGH: 'bg-orange-500',
  CRITICAL: 'bg-red-600',
}

const ScanResult: React.FC<Props> = ({ result }) => {
  const [showDetails, setShowDetails] = useState(false)

  const topFeatures = Object.entries(result.feature_importance)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .map(([name, value]) => ({ name, value: parseFloat(value.toFixed(4)) }))

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2))
    toast.success('Copied to clipboard')
  }

  const scoreColor =
    result.risk_score < 31 ? '#22c55e' :
    result.risk_score < 61 ? '#eab308' :
    result.risk_score < 86 ? '#f97316' : '#ef4444'

  return (
    <div className={clsx('rounded-xl border-2 p-6 space-y-4', RISK_COLORS[result.risk_level])}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={clsx('px-3 py-1 rounded-full text-white text-sm font-bold', RISK_BADGE[result.risk_level])}>
            {result.risk_level}
          </span>
          <span className="text-white font-semibold">
            {result.is_phishing ? '🚨 Phishing Detected' : '✅ Appears Safe'}
          </span>
        </div>
        <button onClick={handleCopy} title="Copy result" className="text-gray-400 hover:text-white">
          <ClipboardDocumentIcon className="h-5 w-5" />
        </button>
      </div>

      {/* URL */}
      <p className="text-gray-300 text-sm break-all">{result.url}</p>

      {/* Score */}
      <div className="flex items-center gap-6">
        <div className="text-center">
          <div className="text-4xl font-black" style={{ color: scoreColor }}>{result.risk_score}</div>
          <div className="text-xs text-gray-400 mt-1">Risk Score</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-white">{(result.confidence * 100).toFixed(1)}%</div>
          <div className="text-xs text-gray-400 mt-1">Confidence</div>
        </div>
        <div className="text-center">
          <div className="text-lg text-gray-300">{result.scan_time_ms}ms</div>
          <div className="text-xs text-gray-400 mt-1">Scan Time</div>
        </div>
      </div>

      {/* Feature importance chart */}
      {topFeatures.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Top Feature Importance</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={topFeatures} layout="vertical">
              <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#9ca3af', fontSize: 10 }} width={160} />
              <Tooltip contentStyle={{ background: '#1f2937', border: 'none', color: '#fff' }} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {topFeatures.map((_, i) => (
                  <Cell key={i} fill={scoreColor} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Technical details accordion */}
      <button
        onClick={() => setShowDetails((v) => !v)}
        className="flex items-center gap-1 text-sm text-gray-400 hover:text-white"
      >
        {showDetails ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
        Technical Details
      </button>
      {showDetails && (
        <div className="bg-gray-950/60 rounded-lg p-4 text-xs text-gray-300 max-h-64 overflow-y-auto">
          <pre>{JSON.stringify(result.features, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

export default ScanResult
