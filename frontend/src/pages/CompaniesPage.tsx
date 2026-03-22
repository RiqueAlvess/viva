import { Link } from 'react-router-dom'
import { Plus, Building2, CheckCircle, XCircle } from 'lucide-react'
import { useCompanies } from '@/hooks/useCompanies'

export default function CompaniesPage() {
  const { data: companies, isLoading } = useCompanies()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Empresas</h2>
          <p className="text-slate-500 text-sm mt-1">{companies?.length ?? 0} empresas cadastradas</p>
        </div>
        <Link
          to="/dashboard/admin/companies/new"
          className="flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Nova Empresa
        </Link>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 p-5 animate-pulse">
              <div className="h-4 bg-slate-200 rounded w-3/4 mb-3" />
              <div className="h-3 bg-slate-100 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : companies?.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
          <Building2 className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Nenhuma empresa cadastrada</p>
          <Link to="/dashboard/admin/companies/new" className="text-blue-600 text-sm mt-2 inline-block hover:underline">
            Cadastrar primeira empresa
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies?.map((company: any) => (
            <Link
              key={company.id}
              to={`/dashboard/admin/companies/${company.id}`}
              className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                  <Building2 className="w-5 h-5 text-blue-600" />
                </div>
                {company.ativo ? (
                  <span className="flex items-center gap-1 text-xs text-green-600 font-medium">
                    <CheckCircle className="w-3 h-3" /> Ativo
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-xs text-red-500 font-medium">
                    <XCircle className="w-3 h-3" /> Inativo
                  </span>
                )}
              </div>
              <p className="font-semibold text-slate-900 truncate">{company.nome}</p>
              <p className="text-sm text-slate-500 mt-1">CNPJ: {company.cnpj}</p>
              {company.cnae && (
                <p className="text-xs text-slate-400 mt-0.5">CNAE: {company.cnae}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
