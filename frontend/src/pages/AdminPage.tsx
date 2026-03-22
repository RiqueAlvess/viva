import { useQuery } from '@tanstack/react-query'
import { Building2, Users, BarChart3, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '@/services/api'

export default function AdminPage() {
  const { data: stats } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: async () => {
      const res = await api.get('/admin/stats')
      return res.data
    },
  })

  const cards = [
    {
      title: 'Total de Empresas',
      value: stats?.total_companies ?? '—',
      icon: Building2,
      color: 'text-blue-600 bg-blue-50',
      href: '/dashboard/admin/companies',
    },
    {
      title: 'Total de Usuários',
      value: stats?.total_users ?? '—',
      icon: Users,
      color: 'text-green-600 bg-green-50',
      href: '/dashboard/admin/users',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Painel Administrativo</h2>
        <p className="text-slate-500 text-sm mt-1">Visão geral do sistema VIVA</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <Link
            key={card.title}
            to={card.href}
            className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow"
          >
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${card.color} mb-3`}>
              <card.icon className="w-5 h-5" />
            </div>
            <p className="text-2xl font-bold text-slate-900">{card.value}</p>
            <p className="text-sm text-slate-500 mt-1">{card.title}</p>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link
          to="/dashboard/admin/companies/new"
          className="bg-blue-700 text-white rounded-xl p-5 hover:bg-blue-800 transition-colors"
        >
          <Building2 className="w-6 h-6 mb-2" />
          <p className="font-semibold">Nova Empresa</p>
          <p className="text-blue-200 text-sm mt-1">Cadastrar uma nova empresa no sistema</p>
        </Link>
        <Link
          to="/dashboard/campaigns"
          className="bg-white border border-slate-200 rounded-xl p-5 hover:shadow-md transition-shadow"
        >
          <BarChart3 className="w-6 h-6 text-blue-600 mb-2" />
          <p className="font-semibold text-slate-900">Ver Campanhas</p>
          <p className="text-slate-500 text-sm mt-1">Gerenciar campanhas de todas as empresas</p>
        </Link>
      </div>
    </div>
  )
}
