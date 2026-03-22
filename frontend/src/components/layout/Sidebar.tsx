import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Building2,
  Users,
  BarChart3,
  FileText,
  Settings,
  LogOut,
  ShieldCheck,
  ChevronRight,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/auth.service'
import toast from 'react-hot-toast'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
    isActive
      ? 'bg-blue-50 text-blue-700'
      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
  }`

export default function Sidebar() {
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await authService.logout()
    } catch {
      // ignore
    }
    clearAuth()
    navigate('/login')
    toast.success('Logout realizado com sucesso')
  }

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-700 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900">VIVA</p>
            <p className="text-xs text-slate-500">Psicossocial NR-1</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {user?.role === 'ADM' && (
          <>
            <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Administração
            </p>
            <NavLink to="/dashboard/admin" end className={navLinkClass}>
              <LayoutDashboard className="w-4 h-4" />
              Painel Admin
            </NavLink>
            <NavLink to="/dashboard/admin/companies" className={navLinkClass}>
              <Building2 className="w-4 h-4" />
              Empresas
            </NavLink>
            <NavLink to="/dashboard/admin/users" className={navLinkClass}>
              <Users className="w-4 h-4" />
              Todos Usuários
            </NavLink>
            <div className="my-3 border-t border-slate-100" />
          </>
        )}

        <p className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
          Gestão
        </p>
        <NavLink to="/dashboard/campaigns" className={navLinkClass}>
          <BarChart3 className="w-4 h-4" />
          Campanhas
        </NavLink>
        {(user?.role === 'ADM' || user?.role === 'RH') && (
          <NavLink to="/dashboard/users" className={navLinkClass}>
            <Users className="w-4 h-4" />
            Usuários
          </NavLink>
        )}
      </nav>

      {/* User section */}
      <div className="px-3 py-4 border-t border-slate-200 space-y-1">
        <NavLink to="/dashboard/profile" className={navLinkClass}>
          <Settings className="w-4 h-4" />
          Perfil
        </NavLink>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-red-50 hover:text-red-600 transition-colors w-full text-left"
        >
          <LogOut className="w-4 h-4" />
          Sair
        </button>
      </div>

      {/* User info */}
      <div className="px-4 py-3 bg-slate-50 border-t border-slate-200">
        <p className="text-xs font-medium text-slate-900 truncate">{user?.nome}</p>
        <p className="text-xs text-slate-500 truncate">{user?.email}</p>
        <span className="inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
          {user?.role}
        </span>
      </div>
    </aside>
  )
}
