import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import BulkScanner from './components/BulkScanner'
import Statistics from './components/Statistics'
import URLScannerComponent from './components/URLScanner'
import ScanResultComponent from './components/ScanResult'
import { useScanner } from './hooks/useScanner'

const ScanPage: React.FC = () => {
  const { result, loading, scan } = useScanner()

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-white">URL Scanner</h2>
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 space-y-4">
        <URLScannerComponent onScan={scan} loading={loading} />
        {result && <ScanResultComponent result={result} />}
      </div>
    </div>
  )
}

const App: React.FC = () => (
  <BrowserRouter>
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scan" element={<ScanPage />} />
            <Route path="/bulk" element={<BulkScanner />} />
            <Route path="/stats" element={<Statistics />} />
          </Routes>
        </main>
      </div>
    </div>
  </BrowserRouter>
)

export default App
