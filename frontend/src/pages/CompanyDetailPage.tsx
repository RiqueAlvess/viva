import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Building2, Edit2 } from 'lucide-react'
import { useCompany } from '@/hooks/useCompanies'

export default function CompanyDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: company, isLoading } = useCompany(id!)

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-slate-200 rounded w-48" />
        <div className="h-48 bg-slate-200 rounded-xl" />
      </div>
    )
  }

  if (!company) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-500">Empresa não encontrada</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar
      </button>

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">{company.nome}</h2>
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          company.ativo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'
        }`}>
          {company.ativo ? 'Ativo' : 'Inativo'}
        </span>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">CNPJ</p>
            <p className="text-sm text-slate-900 mt-1">{company.cnpj}</p>
          </div>
          {company.cnae && (
            <div>
              <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">CNAE</p>
              <p className="text-sm text-slate-900 mt-1">{company.cnae}</p>
            </div>
          )}
          <div>
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Criada em</p>
            <p className="text-sm text-slate-900 mt-1">
              {new Date(company.created_at).toLocaleDateString('pt-BR')}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
