import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft, Upload, BarChart3, Users, Send, Play, XCircle,
  Building2, CheckCircle, Clock, AlertCircle
} from 'lucide-react'
import { useCampaign, useActivateCampaign, useCloseCampaign } from '@/hooks/useCampaigns'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { useAuthStore } from '@/store/authStore'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/services/api'
import toast from 'react-hot-toast'

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  draft: { label: 'Rascunho', color: 'bg-slate-100 text-slate-600', icon: Clock },
  active: { label: 'Ativa', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  closed: { label: 'Encerrada', color: 'bg-blue-100 text-blue-700', icon: AlertCircle },
}

type TabType = 'overview' | 'hierarchy' | 'invitations' | 'dashboard'

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [confirmClose, setConfirmClose] = useState(false)

  const { data: campaign, isLoading } = useCampaign(id!)
  const { mutate: activate, isPending: activating } = useActivateCampaign()
  const { mutate: close, isPending: closing } = useCloseCampaign()

  const { data: stats } = useQuery({
    queryKey: ['invitations', id, 'stats'],
    queryFn: async () => {
      const res = await api.get(`/invitations/${id}/stats`)
      return res.data
    },
    enabled: !!id,
  })

  const sendInvitations = useMutation({
    mutationFn: async () => {
      const res = await api.post(`/invitations/${id}/send`, { send_all: true })
      return res.data
    },
    onSuccess: (data) => toast.success(data.message),
    onError: (error: any) => toast.error(error?.response?.data?.detail || 'Erro ao enviar convites'),
  })

  const generateReport = useMutation({
    mutationFn: async () => {
      const res = await api.post('/reports/generate', { campaign_id: id })
      return res.data
    },
    onSuccess: () => toast.success('Relatório em geração, aguarde alguns minutos'),
    onError: (error: any) => toast.error(error?.response?.data?.detail || 'Erro ao gerar relatório'),
  })

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-slate-200 rounded w-64" />
        <div className="h-48 bg-slate-200 rounded-xl" />
      </div>
    )
  }

  if (!campaign) {
    return <div className="text-center py-16 text-slate-500">Campanha não encontrada</div>
  }

  const status = STATUS_CONFIG[campaign.status] || STATUS_CONFIG.draft
  const StatusIcon = status.icon
  const canEdit = user?.role === 'ADM' || user?.role === 'RH'

  const tabs: { key: TabType; label: string; icon: any }[] = [
    { key: 'overview', label: 'Visão Geral', icon: BarChart3 },
    { key: 'hierarchy', label: 'Hierarquia', icon: Building2 },
    { key: 'invitations', label: 'Convites', icon: Users },
    { key: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  ]

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar
      </button>

      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-bold text-slate-900">{campaign.nome}</h2>
              <span className={`flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${status.color}`}>
                <StatusIcon className="w-3 h-3" />
                {status.label}
              </span>
            </div>
            {campaign.descricao && <p className="text-sm text-slate-500 mb-2">{campaign.descricao}</p>}
            <p className="text-xs text-slate-400">
              {format(new Date(campaign.data_inicio), "dd/MM/yyyy", { locale: ptBR })}
              {' — '}
              {format(new Date(campaign.data_fim), "dd/MM/yyyy", { locale: ptBR })}
            </p>
          </div>

          {canEdit && (
            <div className="flex items-center gap-2 flex-wrap">
              {campaign.status === 'draft' && (
                <>
                  <Link
                    to={`/dashboard/campaigns/${id}/upload`}
                    className="flex items-center gap-2 px-3 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50"
                  >
                    <Upload className="w-4 h-4" />
                    Upload CSV
                  </Link>
                  <button
                    onClick={() => activate(id!)}
                    disabled={activating}
                    className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-60"
                  >
                    <Play className="w-4 h-4" />
                    Ativar
                  </button>
                </>
              )}
              {campaign.status === 'active' && (
                <>
                  <button
                    onClick={() => sendInvitations.mutate()}
                    disabled={sendInvitations.isPending}
                    className="flex items-center gap-2 px-3 py-2 bg-blue-700 text-white rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-60"
                  >
                    <Send className="w-4 h-4" />
                    Enviar Convites
                  </button>
                  <button
                    onClick={() => confirmClose ? close(id!) : setConfirmClose(true)}
                    disabled={closing}
                    className="flex items-center gap-2 px-3 py-2 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600 disabled:opacity-60"
                  >
                    <XCircle className="w-4 h-4" />
                    {confirmClose ? 'Confirmar Encerramento' : 'Encerrar'}
                  </button>
                </>
              )}
              {campaign.status !== 'draft' && (
                <button
                  onClick={() => generateReport.mutate()}
                  disabled={generateReport.isPending}
                  className="flex items-center gap-2 px-3 py-2 border border-slate-300 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-50 disabled:opacity-60"
                >
                  Gerar Relatório PDF
                </button>
              )}
            </div>
          )}
        </div>

        {/* Quick stats */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 pt-4 border-t border-slate-100">
            {[
              { label: 'Total Convidados', value: stats.total },
              { label: 'Enviados', value: stats.sent },
              { label: 'Respondidos', value: stats.responded },
              { label: 'Pendentes', value: stats.pending },
            ].map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-2xl font-bold text-slate-900">{s.value}</p>
                <p className="text-xs text-slate-500 mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-700 text-blue-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      {activeTab === 'overview' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <p className="text-sm text-slate-500">
            Campanha criada em{' '}
            {format(new Date(campaign.created_at), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}.
          </p>
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-xs text-slate-500 uppercase font-medium tracking-wide mb-1">Status</p>
              <p className="text-slate-900">{status.label}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase font-medium tracking-wide mb-1">Empresa ID</p>
              <p className="text-slate-900 font-mono text-xs">{campaign.company_id}</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'dashboard' && (
        <div className="text-center py-8">
          <Link
            to={`/dashboard/campaigns/${id}/analytics`}
            className="inline-flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800"
          >
            <BarChart3 className="w-4 h-4" />
            Ver Analytics Completo
          </Link>
        </div>
      )}

      {activeTab === 'hierarchy' && (
        <HierarchyTab campaignId={id!} />
      )}

      {activeTab === 'invitations' && (
        <InvitationsTab campaignId={id!} />
      )}
    </div>
  )
}

function HierarchyTab({ campaignId }: { campaignId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['campaigns', campaignId, 'hierarchy'],
    queryFn: async () => {
      const res = await api.get(`/campaigns/${campaignId}/hierarchy`)
      return res.data
    },
  })

  if (isLoading) return <div className="animate-pulse h-48 bg-slate-200 rounded-xl" />

  if (!data?.units?.length) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 text-center">
        <Building2 className="w-8 h-8 text-slate-300 mx-auto mb-2" />
        <p className="text-slate-500 text-sm">Nenhuma hierarquia importada ainda.</p>
        <Link
          to={`/dashboard/campaigns/${campaignId}/upload`}
          className="text-blue-600 text-sm hover:underline mt-1 inline-block"
        >
          Fazer upload do CSV
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {data.units.map((unit: any) => (
        <div key={unit.id} className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="font-semibold text-slate-900 mb-2">{unit.nome}</p>
          <div className="space-y-2 pl-4">
            {unit.sectors?.map((sector: any) => (
              <div key={sector.id} className="text-sm">
                <p className="text-slate-700 font-medium">{sector.nome}</p>
                <div className="pl-4 space-y-1 mt-1">
                  {sector.positions?.map((pos: any) => (
                    <p key={pos.id} className="text-slate-500 text-xs">
                      {pos.nome} <span className="text-slate-400">({pos.collaborator_count} colaboradores)</span>
                    </p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function InvitationsTab({ campaignId }: { campaignId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['invitations', campaignId, 'list'],
    queryFn: async () => {
      const res = await api.get(`/invitations/${campaignId}/list`)
      return res.data
    },
  })

  if (isLoading) return <div className="animate-pulse h-48 bg-slate-200 rounded-xl" />

  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    sent: 'bg-blue-100 text-blue-700',
    responded: 'bg-green-100 text-green-700',
    expired: 'bg-red-100 text-red-600',
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {!data?.length ? (
        <div className="p-6 text-center text-slate-500 text-sm">Nenhum convite enviado ainda.</div>
      ) : (
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Email Hash</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Enviado em</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Expira em</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.map((inv: any) => (
              <tr key={inv.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-mono text-xs text-slate-600">{inv.email_hash?.slice(0, 16)}...</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusColors[inv.display_status] || 'bg-slate-100 text-slate-600'}`}>
                    {inv.display_status}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-500 text-xs">
                  {inv.sent_at ? format(new Date(inv.sent_at), "dd/MM/yyyy HH:mm") : '—'}
                </td>
                <td className="px-4 py-3 text-slate-500 text-xs">
                  {format(new Date(inv.expires_at), "dd/MM/yyyy HH:mm")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
