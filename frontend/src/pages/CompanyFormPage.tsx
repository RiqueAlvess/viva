import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { useCreateCompany } from '@/hooks/useCompanies'

const schema = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  cnpj: z.string().min(14, 'CNPJ inválido').max(18, 'CNPJ inválido'),
  cnae: z.string().optional(),
  ativo: z.boolean().default(true),
})

type FormValues = z.infer<typeof schema>

export default function CompanyFormPage() {
  const navigate = useNavigate()
  const { mutate: create, isPending } = useCreateCompany()

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { ativo: true },
  })

  const onSubmit = (data: FormValues) => {
    create(data, {
      onSuccess: () => navigate('/dashboard/admin/companies'),
    })
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

      <h2 className="text-2xl font-bold text-slate-900 mb-6">Nova Empresa</h2>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Nome da Empresa *</label>
            <input
              {...register('nome')}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Empresa ABC Ltda"
            />
            {errors.nome && <p className="text-red-500 text-xs mt-1">{errors.nome.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">CNPJ *</label>
            <input
              {...register('cnpj')}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="00.000.000/0000-00"
            />
            {errors.cnpj && <p className="text-red-500 text-xs mt-1">{errors.cnpj.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">CNAE</label>
            <input
              {...register('cnae')}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="6201-5/01"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              {...register('ativo')}
              type="checkbox"
              id="ativo"
              className="h-4 w-4 text-blue-600 rounded"
            />
            <label htmlFor="ativo" className="text-sm font-medium text-slate-700">Empresa ativa</label>
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
              Criar Empresa
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
