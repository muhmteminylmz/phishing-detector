import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { bulkScan, getBulkStatus } from '../services/api'
import type { BulkScanStatus } from '../types'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

const BulkScanner: React.FC = () => {
  const [text, setText] = useState('')
  const [taskStatus, setTaskStatus] = useState<BulkScanStatus | null>(null)
  const [loading, setLoading] = useState(false)

  const onDrop = useCallback((accepted: File[]) => {
    const file = accepted[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (e) => setText((e.target?.result as string) ?? '')
    reader.readAsText(file)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/plain': ['.txt'], 'text/csv': ['.csv'] },
    multiple: false,
  })

  const urls = text
    .split('\n')
    .map((u) => u.trim())
    .filter(Boolean)

  const handleScan = async () => {
    if (urls.length === 0) return toast.error('No URLs provided')
    if (urls.length > 100) return toast.error('Maximum 100 URLs allowed')
    setLoading(true)
    try {
      const { task_id } = await bulkScan(urls)
      toast.success('Bulk scan started')
      // Poll for status
      const poll = async () => {
        const status = await getBulkStatus(task_id)
        setTaskStatus(status)
        if (status.status !== 'completed' && status.status !== 'failed') {
          setTimeout(poll, 2000)
        }
      }
      await poll()
    } catch (err) {
      toast.error('Bulk scan failed')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    if (!taskStatus?.results) return
    const rows = taskStatus.results.map((r: Record<string, unknown>) =>
      [r['url'], r['is_phishing'], r['risk_level'], r['risk_score'], r['confidence']].join(',')
    )
    const csv = ['url,is_phishing,risk_level,risk_score,confidence', ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = 'scan_results.csv'
    link.click()
  }

  const progress = taskStatus
    ? Math.round((taskStatus.processed_urls / taskStatus.total_urls) * 100)
    : 0

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-white">Bulk Scanner</h2>

      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 space-y-4">
        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={clsx(
            'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
            isDragActive ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 hover:border-gray-500'
          )}
        >
          <input {...getInputProps()} />
          <p className="text-gray-400">
            {isDragActive ? 'Drop file here...' : 'Drop a .txt or .csv file, or click to upload'}
          </p>
        </div>

        {/* Textarea */}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={8}
          placeholder="Or paste URLs here (one per line)"
          className="w-full rounded-lg bg-gray-800 border border-gray-700 px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
        />

        <div className="flex items-center justify-between">
          <span className="text-gray-400 text-sm">{urls.length} URLs</span>
          <button
            onClick={handleScan}
            disabled={loading || urls.length === 0}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 disabled:cursor-not-allowed text-white font-semibold rounded-lg"
          >
            {loading ? 'Scanning...' : 'Start Bulk Scan'}
          </button>
        </div>
      </div>

      {/* Progress */}
      {taskStatus && (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 space-y-4">
          <div className="flex justify-between text-sm text-gray-400">
            <span>Status: <strong className="text-white">{taskStatus.status}</strong></span>
            <span>{taskStatus.processed_urls} / {taskStatus.total_urls}</span>
          </div>
          <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>

          {taskStatus.results && taskStatus.results.length > 0 && (
            <>
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-green-700 hover:bg-green-600 text-white rounded-lg text-sm"
              >
                Export CSV
              </button>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-gray-400 border-b border-gray-800">
                      <th className="text-left py-2 pr-4">URL</th>
                      <th className="text-left py-2 pr-4">Phishing</th>
                      <th className="text-left py-2 pr-4">Risk</th>
                      <th className="text-left py-2">Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {taskStatus.results.map((r: Record<string, unknown>, i: number) => (
                      <tr key={i} className="border-b border-gray-800/50">
                        <td className="py-1 pr-4 max-w-xs truncate text-gray-300">{r['url'] as string}</td>
                        <td className="py-1 pr-4 text-sm">
                          {r['is_phishing'] ? '🚨' : '✅'}
                        </td>
                        <td className="py-1 pr-4 text-gray-300">{r['risk_level'] as string}</td>
                        <td className="py-1 text-gray-300">{r['risk_score'] as number}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default BulkScanner
