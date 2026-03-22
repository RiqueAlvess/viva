import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Users, UserCheck, UserX } from 'lucide-react'
import api from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

interface UsersPageProps {
  adminView?: boolean
}

export default function UsersPage({ adminView }: UsersPageProps) {
  const user = useAuthStore((s) => s.user)
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ nome: '', email: '', password: '', role: 'LIDERANCA', company_id: '' })

  const endpoint = adminView ? '/admin/users' : '/users/'
  const { data: users, isLoading } = useQuery({
    queryKey: ['users', adminView ? 'all' : user?.company_id],
    queryFn: async () => {
      const res = await api.get(endpoint)
      return res.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const endpoint = user?.role === 'ADM'
        ? '/users/'
        : '/users/rh-create'
      const res = await api.post(endpoint, data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast.success('Usuário criado com sucesso')
      setShowForm(false)
      setForm({ nome: '', email: '', password: '', role: 'LIDERANCA', company_id: '' })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao criar usuário')
    },
  })

  const toggleActive = useMutation({
    mutationFn: async ({ id, ativo }: { id: string; ativo: boolean }) => {
      const res = await api.patch(`/users/${id}`, { ativo })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao atualizar usuário')
    },
  })

  const roleColors: Record<string, string> = {
    ADM: 'bg-purple-100 text-purple-700',
    RH: 'bg-blue-100 text-blue-700',
    LIDERANCA: 'bg-green-100 text-green-700',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            {adminView ? 'Todos os Usuários' : 'Usuários'}
          </h2>
          <p className="text-slate-500 text-sm mt-1">{users?.length ?? 0} usuários</p>
        </div>
        {!adminView && (user?.role === 'ADM' || user?.role === 'RH') && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Novo Usuário
          </button>
        )}
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-4">Novo Usuário</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Nome *</label>
              <input
                value={form.nome}
                onChange={(e) => setForm((f) => ({ ...f, nome: e.target.value }))}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email *</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Senha *</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {user?.role === 'ADM' && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Perfil</label>
                <select
                  value={form.role}
                  onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="RH">RH</option>
                  <option value="LIDERANCA">Liderança</option>
                  <option value="ADM">Administrador</option>
                </select>
              </div>
            )}
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50"
            >
              Cancelar
            </button>
            <button
              onClick={() => createMutation.mutate(form)}
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-blue-700 text-white rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-60"
            >
              Criar
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="p-4 animate-pulse flex items-center gap-3">
              <div className="w-8 h-8 bg-slate-200 rounded-full" />
              <div className="flex-1">
                <div className="h-4 bg-slate-200 rounded w-32 mb-2" />
                <div className="h-3 bg-slate-100 rounded w-48" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Nome</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Email</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Perfil</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
                {!adminView && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users?.map((u: any) => (
                <tr key={u.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{u.nome}</td>
                  <td className="px-4 py-3 text-slate-500">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${roleColors[u.role] || 'bg-slate-100 text-slate-600'}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`flex items-center gap-1 text-xs font-medium w-fit ${u.ativo ? 'text-green-600' : 'text-red-500'}`}>
                      {u.ativo ? <UserCheck className="w-3 h-3" /> : <UserX className="w-3 h-3" />}
                      {u.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  {!adminView && (
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => toggleActive.mutate({ id: u.id, ativo: !u.ativo })}
                        className="text-xs text-slate-500 hover:text-slate-700"
                      >
                        {u.ativo ? 'Desativar' : 'Ativar'}
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
