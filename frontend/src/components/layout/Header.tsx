import { useLocation } from 'react-router-dom'
import { Bell } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

const ROUTE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/dashboard/admin': 'Painel Administrativo',
  '/dashboard/admin/companies': 'Empresas',
  '/dashboard/admin/companies/new': 'Nova Empresa',
  '/dashboard/admin/users': 'Todos os Usuários',
  '/dashboard/campaigns': 'Campanhas',
  '/dashboard/campaigns/new': 'Nova Campanha',
  '/dashboard/users': 'Usuários',
  '/dashboard/profile': 'Perfil',
}

function getTitle(pathname: string): string {
  if (ROUTE_TITLES[pathname]) return ROUTE_TITLES[pathname]
  if (pathname.includes('/analytics')) return 'Analytics'
  if (pathname.includes('/upload')) return 'Upload CSV'
  if (pathname.includes('/campaigns/')) return 'Detalhe da Campanha'
  if (pathname.includes('/admin/companies/')) return 'Detalhe da Empresa'
  return 'VIVA Psicossocial'
}

export default function Header() {
  const location = useLocation()
  const user = useAuthStore((s) => s.user)
  const title = getTitle(location.pathname)

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <h1 className="text-lg font-semibold text-slate-900">{title}</h1>
      <div className="flex items-center gap-4">
        <button className="relative p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors">
          <Bell className="w-5 h-5" />
        </button>
        <div className="w-8 h-8 rounded-full bg-blue-700 flex items-center justify-center text-white text-sm font-medium">
          {user?.nome?.charAt(0).toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  )
}
