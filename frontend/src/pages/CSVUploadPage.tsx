import { useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Upload, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import api from '@/services/api'
import toast from 'react-hot-toast'

export default function CSVUploadPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const fileRef = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState<any>(null)
  const [file, setFile] = useState<File | null>(null)

  const previewMutation = useMutation({
    mutationFn: async (f: File) => {
      const form = new FormData()
      form.append('file', f)
      const res = await api.post(`/campaigns/${id}/preview-csv`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return res.data
    },
    onSuccess: (data) => setPreview(data),
    onError: (error: any) => toast.error(error?.response?.data?.detail || 'Erro ao processar CSV'),
  })

  const uploadMutation = useMutation({
    mutationFn: async (f: File) => {
      const form = new FormData()
      form.append('file', f)
      const res = await api.post(`/campaigns/${id}/upload-csv`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return res.data
    },
    onSuccess: (data) => {
      toast.success(`Importados ${data.collaborators} colaboradores`)
      navigate(`/dashboard/campaigns/${id}`)
    },
    onError: (error: any) => toast.error(error?.response?.data?.detail || 'Erro ao importar CSV'),
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) {
      setFile(f)
      previewMutation.mutate(f)
    }
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

      <h2 className="text-2xl font-bold text-slate-900 mb-2">Upload de Colaboradores</h2>
      <p className="text-slate-500 text-sm mb-6">
        Importe colaboradores via arquivo CSV. O arquivo deve ter as colunas: <code className="bg-slate-100 px-1 rounded">unidade, setor, cargo, email</code>.
      </p>

      {/* Upload area */}
      <div
        onClick={() => fileRef.current?.click()}
        className="bg-white border-2 border-dashed border-slate-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors mb-4"
      >
        <Upload className="w-8 h-8 text-slate-400 mx-auto mb-3" />
        <p className="text-slate-700 font-medium mb-1">
          {file ? file.name : 'Clique para selecionar o arquivo CSV'}
        </p>
        <p className="text-slate-400 text-sm">Formatos aceitos: .csv (separador ; ou ,)</p>
        <input
          ref={fileRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {previewMutation.isPending && (
        <div className="flex items-center gap-2 text-slate-500 text-sm py-4">
          <Loader2 className="w-4 h-4 animate-spin" />
          Analisando arquivo...
        </div>
      )}

      {preview && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 mb-4">
          <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Prévia da Importação
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-4">
            {[
              { label: 'Total de Linhas', value: preview.total_rows },
              { label: 'Unidades', value: preview.units },
              { label: 'Setores', value: preview.sectors },
              { label: 'Cargos', value: preview.positions },
              { label: 'Colaboradores', value: preview.collaborators },
            ].map((s) => (
              <div key={s.label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-2xl font-bold text-slate-900">{s.value}</p>
                <p className="text-xs text-slate-500 mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>

          {preview.errors?.length > 0 && (
            <div className="bg-red-50 rounded-lg p-3 mb-4">
              <p className="text-sm font-medium text-red-700 flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4" />
                {preview.errors.length} erro(s) encontrado(s)
              </p>
              <ul className="text-xs text-red-600 space-y-1">
                {preview.errors.slice(0, 5).map((err: string, i: number) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          <button
            onClick={() => file && uploadMutation.mutate(file)}
            disabled={uploadMutation.isPending || preview.errors?.length > 0}
            className="w-full flex items-center justify-center gap-2 bg-blue-700 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-60 transition-colors"
          >
            {uploadMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            {uploadMutation.isPending ? 'Importando...' : 'Confirmar Importação'}
          </button>
        </div>
      )}
    </div>
  )
}
