import React from 'react'
import { ShieldCheckIcon } from '@heroicons/react/24/solid'

const Header: React.FC = () => (
  <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center gap-3">
    <ShieldCheckIcon className="h-8 w-8 text-blue-500" />
    <div>
      <h1 className="text-xl font-bold text-white">Phishing Detector</h1>
      <p className="text-xs text-gray-400">ML-powered URL analysis</p>
    </div>
  </header>
)

export default Header
