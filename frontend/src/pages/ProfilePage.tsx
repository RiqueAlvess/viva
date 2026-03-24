import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import api from '@/services/api'
import toast from 'react-hot-toast'
import { Loader2, User } from 'lucide-react'

export default function ProfilePage() {
  const { user, setAuth, accessToken } = useAuthStore()
  const [form, setForm] = useState({ nome: user?.nome || '', password: '', confirm: '' })

  const updateMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await api.patch(`/users/${user?.id}`, data)
      return res.data
    },
    onSuccess: (updatedUser) => {
      if (accessToken) {
        setAuth(updatedUser, accessToken)
      }
      toast.success('Perfil atualizado')
      setForm((f) => ({ ...f, password: '', confirm: '' }))
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao atualizar perfil')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (form.password && form.password !== form.confirm) {
      toast.error('As senhas não coincidem')
      return
    }
    const data: any = { nome: form.nome }
    if (form.password) data.password = form.password
    updateMutation.mutate(data)
  }

  const roleLabels: Record<string, string> = {
    ADM: 'Administrador',
    RH: 'Recursos Humanos',
    LIDERANCA: 'Liderança',
  }

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Meu Perfil</h2>
        <p className="text-slate-500 text-sm mt-1">Gerencie suas informações pessoais</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-blue-700 flex items-center justify-center text-white text-xl font-bold">
            {user?.nome?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div>
            <p className="font-semibold text-slate-900">{user?.nome}</p>
            <p className="text-sm text-slate-500">{user?.email}</p>
            <span className="inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
              {roleLabels[user?.role || ''] || user?.role}
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Nome</label>
            <input
              value={form.nome}
              onChange={(e) => setForm((f) => ({ ...f, nome: e.target.value }))}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">E-mail</label>
            <input
              value={user?.email}
              disabled
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-slate-50 text-slate-400 cursor-not-allowed"
            />
          </div>

          <hr className="border-slate-100" />

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Nova Senha</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Deixe em branco para não alterar"
            />
          </div>

          {form.password && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Confirmar Senha</label>
              <input
                type="password"
                value={form.confirm}
                onChange={(e) => setForm((f) => ({ ...f, confirm: e.target.value }))}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="w-full flex items-center justify-center gap-2 bg-blue-700 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-60 transition-colors"
          >
            {updateMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            Salvar Alterações
          </button>
        </form>
      </div>
    </div>
  )
}
