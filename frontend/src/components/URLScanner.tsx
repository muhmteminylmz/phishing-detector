import React, { useState } from 'react'
import { MagnifyingGlassIcon } from '@heroicons/react/24/solid'

interface Props {
  onScan: (url: string) => void
  loading: boolean
}

const URLScanner: React.FC<Props> = ({ onScan, loading }) => {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) return
    onScan(trimmed)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL to scan (e.g. https://example.com)"
        className="flex-1 rounded-lg bg-gray-800 border border-gray-700 px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !url.trim()}
        className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
      >
        {loading ? (
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
        ) : (
          <MagnifyingGlassIcon className="h-5 w-5" />
        )}
        {loading ? 'Scanning...' : 'Scan'}
      </button>
    </form>
  )
}

export default URLScanner
