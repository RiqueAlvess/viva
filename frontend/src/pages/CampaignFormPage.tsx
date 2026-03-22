import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { useCreateCampaign } from '@/hooks/useCampaigns'
import { useAuthStore } from '@/store/authStore'
import { useCompanies } from '@/hooks/useCompanies'

const schema = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  descricao: z.string().optional(),
  data_inicio: z.string().min(1, 'Data de início é obrigatória'),
  data_fim: z.string().min(1, 'Data de fim é obrigatória'),
  company_id: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

export default function CampaignFormPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const { mutate: create, isPending } = useCreateCampaign()
  const { data: companies } = useCompanies()

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  const onSubmit = (data: FormValues) => {
    create(
      {
        ...data,
        data_inicio: new Date(data.data_inicio).toISOString(),
        data_fim: new Date(data.data_fim).toISOString(),
      },
      { onSuccess: (campaign: any) => navigate(`/dashboard/campaigns/${campaign.id}`) }
    )
  }

  return (
    <div className="max-w-lg">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar
      </button>

      <h2 className="text-2xl font-bold text-slate-900 mb-6">Nova Campanha</h2>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {user?.role === 'ADM' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Empresa *</label>
              <select
                {...register('company_id')}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Selecione uma empresa</option>
                {companies?.map((c: any) => (
                  <option key={c.id} value={c.id}>{c.nome}</option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Nome da Campanha *</label>
            <input
              {...register('nome')}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Pesquisa de Clima 2024"
            />
            {errors.nome && <p className="text-red-500 text-xs mt-1">{errors.nome.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Descrição</label>
            <textarea
              {...register('descricao')}
              rows={3}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="Descrição opcional da campanha..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Data Início *</label>
              <input
                {...register('data_inicio')}
                type="date"
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.data_inicio && <p className="text-red-500 text-xs mt-1">{errors.data_inicio.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Data Fim *</label>
              <input
                {...register('data_fim')}
                type="date"
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.data_fim && <p className="text-red-500 text-xs mt-1">{errors.data_fim.message}</p>}
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex-1 border border-slate-300 text-slate-700 py-2 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="flex-1 flex items-center justify-center gap-2 bg-blue-700 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-60 transition-colors"
            >
              {isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              Criar Campanha
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
