import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Database, BarChart3, Upload,
  Brain, Settings, PieChart, FileText, Activity, TrendingUp, CreditCard,
  CloudDownload, Cpu,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Logo } from './Logo'

const navItems = [
  { label: 'Tableau de bord', href: '/', icon: LayoutDashboard, exact: true },
  { label: 'Collecte API (Officiel)', href: '/collection', icon: CloudDownload },
  { label: 'Datasets & Sources', href: '/datasets', icon: Database },
  { label: 'Import Fichiers', href: '/import', icon: Upload },
  { label: 'Formulaires Terrain', href: '/forms', icon: FileText },
  { label: 'Analyses & Gemini IA', href: '/analysis', icon: BarChart3 },
  { label: 'Modèles ML', href: '/models', icon: Cpu },
  { label: 'Abonnements', href: '/pricing', icon: CreditCard },
  { label: 'Paramètres', href: '/settings', icon: Settings },
]

export function Sidebar() {
  return (
    <aside className="hidden md:flex flex-col w-64 border-r bg-white dark:bg-gray-950 shadow-sm">
      {/* Brand */}
      <div className="p-5 border-b bg-gradient-to-r from-[#007A5E] to-[#005a45]">
        <div className="flex items-center gap-3">
          <Logo size={36} />
          <div>
            <h1 className="font-bold text-lg text-white leading-tight">DataCollect</h1>
            <p className="text-xs text-green-200 font-medium">Pro Cameroun</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.href + item.label}
              to={item.href}
              end={item.exact}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-[#007A5E] text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-900 hover:text-gray-900 dark:hover:text-gray-100'
                )
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t bg-gray-50 dark:bg-gray-900">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs text-gray-500">Système opérationnel</span>
        </div>
        <div className="flex gap-1 mt-2">
          <div className="h-1 flex-1 rounded bg-[#007A5E]" />
          <div className="h-1 flex-1 rounded bg-[#CE1126]" />
          <div className="h-1 flex-1 rounded bg-[#FCD116]" />
        </div>
        <p className="text-xs text-gray-400 mt-1">DataCollect Pro v2.0</p>
      </div>
    </aside>
  )
}
