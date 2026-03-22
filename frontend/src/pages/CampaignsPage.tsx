import { Link } from 'react-router-dom'
import { Plus, BarChart3, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { useCampaigns } from '@/hooks/useCampaigns'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { useAuthStore } from '@/store/authStore'

const statusConfig: Record<string, { label: string; color: string; icon: any }> = {
  draft: { label: 'Rascunho', color: 'bg-slate-100 text-slate-600', icon: Clock },
  active: { label: 'Ativa', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  closed: { label: 'Encerrada', color: 'bg-blue-100 text-blue-700', icon: AlertCircle },
}

export default function CampaignsPage() {
  const { data: campaigns, isLoading } = useCampaigns()
  const user = useAuthStore((s) => s.user)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Campanhas</h2>
          <p className="text-slate-500 text-sm mt-1">{campaigns?.length ?? 0} campanhas</p>
        </div>
        {(user?.role === 'ADM' || user?.role === 'RH') && (
          <Link
            to="/dashboard/campaigns/new"
            className="flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Nova Campanha
          </Link>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 p-5 animate-pulse">
              <div className="h-5 bg-slate-200 rounded w-48 mb-3" />
              <div className="h-3 bg-slate-100 rounded w-64" />
            </div>
          ))}
        </div>
      ) : campaigns?.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
          <BarChart3 className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Nenhuma campanha cadastrada</p>
          {(user?.role === 'ADM' || user?.role === 'RH') && (
            <Link to="/dashboard/campaigns/new" className="text-blue-600 text-sm mt-2 inline-block hover:underline">
              Criar primeira campanha
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {campaigns?.map((campaign: any) => {
            const status = statusConfig[campaign.status] || statusConfig.draft
            const StatusIcon = status.icon
            return (
              <Link
                key={campaign.id}
                to={`/dashboard/campaigns/${campaign.id}`}
                className="block bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-slate-900 truncate">{campaign.nome}</h3>
                      <span className={`shrink-0 flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${status.color}`}>
                        <StatusIcon className="w-3 h-3" />
                        {status.label}
                      </span>
                    </div>
                    {campaign.descricao && (
                      <p className="text-sm text-slate-500 truncate mb-2">{campaign.descricao}</p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span>
                        {format(new Date(campaign.data_inicio), "dd/MM/yyyy", { locale: ptBR })}
                        {' — '}
                        {format(new Date(campaign.data_fim), "dd/MM/yyyy", { locale: ptBR })}
                      </span>
                      {campaign.total_invited != null && (
                        <span>{campaign.total_invited} convidados</span>
                      )}
                      {campaign.total_responded != null && (
                        <span>{campaign.total_responded} responderam</span>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
