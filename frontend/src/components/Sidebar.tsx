import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  HomeIcon,
  MagnifyingGlassIcon,
  TableCellsIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

const links = [
  { to: '/', label: 'Dashboard', Icon: HomeIcon },
  { to: '/scan', label: 'URL Scanner', Icon: MagnifyingGlassIcon },
  { to: '/bulk', label: 'Bulk Scan', Icon: TableCellsIcon },
  { to: '/stats', label: 'Statistics', Icon: ChartBarIcon },
]

const Sidebar: React.FC = () => (
  <nav className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col gap-1 p-4 min-h-screen">
    {links.map(({ to, label, Icon }) => (
      <NavLink
        key={to}
        to={to}
        end={to === '/'}
        className={({ isActive }) =>
          clsx(
            'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            isActive
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:bg-gray-800 hover:text-white'
          )
        }
      >
        <Icon className="h-5 w-5" />
        {label}
      </NavLink>
    ))}
  </nav>
)

export default Sidebar
