import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import { Loader2, TrendingUp, Users, BarChart3 } from 'lucide-react'
import api from '@/services/api'

const RISK_COLORS: Record<string, string> = {
  aceitavel: '#10B981',
  moderado: '#F59E0B',
  importante: '#F97316',
  critico: '#EF4444',
}

const DIMENSION_LABELS: Record<string, string> = {
  demandas: 'Demandas',
  controle: 'Controle',
  apoio_chefia: 'Apoio Chefia',
  apoio_colegas: 'Apoio Colegas',
  relacionamentos: 'Relacionamentos',
  cargo: 'Cargo',
  comunicacao_mudancas: 'Comunicação',
}

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    aceitavel: 'bg-green-100 text-green-700',
    moderado: 'bg-yellow-100 text-yellow-700',
    importante: 'bg-orange-100 text-orange-700',
    critico: 'bg-red-100 text-red-700',
  }
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${colors[level] || 'bg-slate-100 text-slate-600'}`}>
      {level}
    </span>
  )
}

export default function AnalyticsPage() {
  const { id } = useParams<{ id: string }>()

  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ['dashboard', id],
    queryFn: async () => {
      const res = await api.get(`/dashboard/${id}`)
      return res.data
    },
    enabled: !!id,
    retry: 1,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
          <p className="text-slate-500 text-sm">Carregando analytics...</p>
        </div>
      </div>
    )
  }

  if (error || !dashboard) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
        <BarChart3 className="w-10 h-10 text-slate-300 mx-auto mb-3" />
        <p className="text-slate-500">Dados de analytics não disponíveis ainda.</p>
        <p className="text-slate-400 text-sm mt-1">Aguarde respostas serem processadas.</p>
      </div>
    )
  }

  const riskPieData = Object.entries(dashboard.risk_distribution || {}).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: value as number,
    color: RISK_COLORS[key] || '#94A3B8',
  }))

  const dimensionChartData = (dashboard.dimension_scores || []).map((d: any) => ({
    name: DIMENSION_LABELS[d.dimension] || d.dimension,
    score: parseFloat(d.score.toFixed(2)),
    nr_value: parseFloat(d.nr_value.toFixed(2)),
    risk_level: d.risk_level,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">{dashboard.campaign_nome}</h2>
        <p className="text-slate-500 text-sm mt-1">{dashboard.company_nome}</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total Convidados', value: dashboard.total_invited, icon: Users, color: 'text-blue-600 bg-blue-50' },
          { label: 'Responderam', value: dashboard.total_responded, icon: Users, color: 'text-green-600 bg-green-50' },
          { label: 'Taxa de Adesão', value: `${(dashboard.adhesion_rate || 0).toFixed(1)}%`, icon: TrendingUp, color: 'text-orange-600 bg-orange-50' },
          { label: 'IGRP', value: (dashboard.igrp || 0).toFixed(2), icon: BarChart3, color: 'text-purple-600 bg-purple-50' },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-white rounded-xl border border-slate-200 p-4">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${kpi.color} mb-2`}>
              <kpi.icon className="w-4 h-4" />
            </div>
            <p className="text-2xl font-bold text-slate-900">{kpi.value}</p>
            <p className="text-xs text-slate-500 mt-0.5">{kpi.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dimension scores chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-900 mb-4">Score por Dimensão</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={dimensionChartData} layout="vertical" margin={{ left: 80 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 5]} tick={{ fontSize: 12 }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={80} />
              <Tooltip
                formatter={(val: number, name: string) => [val.toFixed(2), name === 'score' ? 'Score' : 'NR Value']}
              />
              <Bar dataKey="score" fill="#3B82F6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Risk distribution pie */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-900 mb-4">Distribuição de Risco</h3>
          {riskPieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={riskPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {riskPieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(val) => [val, 'Ocorrências']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-slate-400 text-sm">
              Sem dados disponíveis
            </div>
          )}
        </div>
      </div>

      {/* Top 5 sectors */}
      {dashboard.top5_sectors?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-900 mb-4">Top 5 Setores com Maior Risco</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left px-3 py-2 text-xs font-semibold text-slate-500 uppercase">Unidade</th>
                  <th className="text-left px-3 py-2 text-xs font-semibold text-slate-500 uppercase">Setor</th>
                  <th className="text-center px-3 py-2 text-xs font-semibold text-slate-500 uppercase">Respostas</th>
                  <th className="text-center px-3 py-2 text-xs font-semibold text-slate-500 uppercase">NR Score</th>
                  <th className="text-center px-3 py-2 text-xs font-semibold text-slate-500 uppercase">Risco</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {dashboard.top5_sectors.map((s: any) => (
                  <tr key={s.sector_id} className="hover:bg-slate-50">
                    <td className="px-3 py-2 text-slate-700">{s.unit_nome}</td>
                    <td className="px-3 py-2 text-slate-700">{s.sector_nome}</td>
                    <td className="px-3 py-2 text-center text-slate-500">{s.response_count}</td>
                    <td className="px-3 py-2 text-center font-medium text-slate-900">{s.avg_nr.toFixed(2)}</td>
                    <td className="px-3 py-2 text-center">
                      <RiskBadge level={s.risk_level} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Demographic data */}
      {dashboard.demographic && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-900 mb-4">Dados Demográficos</h3>
          {!dashboard.demographic.faixa_etaria && !dashboard.demographic.genero ? (
            <p className="text-slate-400 text-sm">Dados demográficos insuficientes (mínimo 5 respostas).</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              {dashboard.demographic.faixa_etaria && (
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase mb-2">Faixa Etária</p>
                  {Object.entries(dashboard.demographic.faixa_etaria).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-sm py-0.5">
                      <span className="text-slate-600">{k}</span>
                      <span className="font-medium text-slate-900">{v as number}</span>
                    </div>
                  ))}
                </div>
              )}
              {dashboard.demographic.genero && (
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase mb-2">Gênero</p>
                  {Object.entries(dashboard.demographic.genero).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-sm py-0.5">
                      <span className="text-slate-600">{k === 'M' ? 'Masculino' : k === 'F' ? 'Feminino' : k === 'O' ? 'Outro' : 'N/I'}</span>
                      <span className="font-medium text-slate-900">{v as number}</span>
                    </div>
                  ))}
                </div>
              )}
              {dashboard.demographic.tempo_empresa && (
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase mb-2">Tempo na Empresa</p>
                  {Object.entries(dashboard.demographic.tempo_empresa).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-sm py-0.5">
                      <span className="text-slate-600">{k} anos</span>
                      <span className="font-medium text-slate-900">{v as number}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
