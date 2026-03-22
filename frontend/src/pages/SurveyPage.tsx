import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Shield, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import api from '@/services/api'
import toast from 'react-hot-toast'

type Step = 'loading' | 'invalid' | 'consent' | 'survey' | 'submitted'

const QUESTIONS = Array.from({ length: 35 }, (_, i) => ({
  id: `q${i + 1}`,
  label: `Questão ${i + 1}`,
}))

const SCALE_LABELS = ['Nunca', 'Raramente', 'Às vezes', 'Frequentemente', 'Sempre']

export default function SurveyPage() {
  const [params] = useSearchParams()
  const token = params.get('token')

  const [step, setStep] = useState<Step>('loading')
  const [sessionData, setSessionData] = useState<any>(null)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [lgpdConsent, setLgpdConsent] = useState(false)
  const [demographics, setDemographics] = useState({
    faixa_etaria: '',
    genero: '',
    tempo_empresa: '',
  })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!token) {
      setStep('invalid')
      return
    }
    api.get(`/survey/validate/${token}`)
      .then((res) => {
        setSessionData(res.data)
        setStep('consent')
      })
      .catch(() => {
        setStep('invalid')
      })
  }, [token])

  const handleSubmit = async () => {
    const unanswered = QUESTIONS.filter((q) => !answers[q.id])
    if (unanswered.length > 0) {
      toast.error(`Responda todas as ${QUESTIONS.length} questões antes de enviar`)
      return
    }
    if (!lgpdConsent) {
      toast.error('É necessário aceitar os termos de privacidade')
      return
    }

    setSubmitting(true)
    try {
      await api.post('/survey/submit', {
        session_uuid: sessionData.session_uuid,
        answers,
        faixa_etaria: demographics.faixa_etaria || null,
        genero: demographics.genero || null,
        tempo_empresa: demographics.tempo_empresa || null,
        lgpd_consent: lgpdConsent,
        unit_id: sessionData.unit_id,
        sector_id: sessionData.sector_id,
      })
      setStep('submitted')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Erro ao enviar respostas')
    } finally {
      setSubmitting(false)
    }
  }

  if (step === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-slate-500">Verificando convite...</p>
        </div>
      </div>
    )
  }

  if (step === 'invalid') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Link inválido ou expirado</h2>
          <p className="text-slate-500">Este link de pesquisa não é válido ou já foi utilizado. Entre em contato com seu RH para receber um novo convite.</p>
        </div>
      </div>
    )
  }

  if (step === 'submitted') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="max-w-md text-center">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Obrigado pela sua participação!</h2>
          <p className="text-slate-500">Suas respostas foram registradas de forma anônima e contribuirão para melhorar o ambiente de trabalho.</p>
        </div>
      </div>
    )
  }

  if (step === 'consent') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="max-w-lg w-full bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="w-8 h-8 text-blue-700" />
            <div>
              <h1 className="text-lg font-bold text-slate-900">Pesquisa de Risco Psicossocial</h1>
              <p className="text-sm text-slate-500">{sessionData?.company_name}</p>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4 mb-6 text-sm text-blue-800 space-y-2">
            <p><strong>Esta pesquisa é completamente anônima.</strong></p>
            <p>Suas respostas não podem ser vinculadas à sua identidade. Os dados são protegidos pela LGPD.</p>
            <p>A pesquisa contém 35 questões e leva aproximadamente 10 minutos.</p>
          </div>

          <label className="flex items-start gap-3 cursor-pointer mb-6">
            <input
              type="checkbox"
              checked={lgpdConsent}
              onChange={(e) => setLgpdConsent(e.target.checked)}
              className="mt-0.5 h-4 w-4 text-blue-600 rounded"
            />
            <span className="text-sm text-slate-700">
              Concordo com o tratamento anônimo dos meus dados para fins de análise de risco psicossocial, conforme a LGPD.
            </span>
          </label>

          <button
            onClick={() => lgpdConsent && setStep('survey')}
            disabled={!lgpdConsent}
            className="w-full bg-blue-700 hover:bg-blue-800 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg transition-colors"
          >
            Iniciar Pesquisa
          </button>
        </div>
      </div>
    )
  }

  // Survey form
  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-4">
          <h2 className="text-lg font-bold text-slate-900 mb-1">Pesquisa de Clima Organizacional</h2>
          <p className="text-sm text-slate-500 mb-6">
            Para cada afirmação, indique com que frequência você experimenta essa situação no trabalho.
          </p>

          {/* Scale header */}
          <div className="grid grid-cols-6 gap-2 mb-4 text-xs text-slate-500 text-center font-medium">
            <div className="text-left">Questão</div>
            {SCALE_LABELS.map((label, i) => (
              <div key={i}>{label}</div>
            ))}
          </div>

          <div className="space-y-3">
            {QUESTIONS.map((q) => (
              <div key={q.id} className="grid grid-cols-6 gap-2 items-center py-2 border-b border-slate-100 last:border-0">
                <div className="text-sm text-slate-700">{q.label}</div>
                {[1, 2, 3, 4, 5].map((val) => (
                  <div key={val} className="flex justify-center">
                    <input
                      type="radio"
                      name={q.id}
                      value={val}
                      checked={answers[q.id] === val}
                      onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: val }))}
                      className="h-4 w-4 text-blue-600 cursor-pointer"
                    />
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Demographics (optional) */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-4">
          <h3 className="text-base font-semibold text-slate-900 mb-4">Dados Demográficos (opcional)</h3>
          <p className="text-sm text-slate-500 mb-4">Esses dados são coletados de forma anônima apenas para análise estatística.</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Faixa Etária</label>
              <select
                value={demographics.faixa_etaria}
                onChange={(e) => setDemographics((d) => ({ ...d, faixa_etaria: e.target.value }))}
                className="w-full border border-slate-300 rounded-lg text-sm py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Prefiro não informar</option>
                {['18-24', '25-34', '35-44', '45-54', '55-64', '65+'].map((v) => (
                  <option key={v} value={v}>{v}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Gênero</label>
              <select
                value={demographics.genero}
                onChange={(e) => setDemographics((d) => ({ ...d, genero: e.target.value }))}
                className="w-full border border-slate-300 rounded-lg text-sm py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Prefiro não informar</option>
                <option value="M">Masculino</option>
                <option value="F">Feminino</option>
                <option value="O">Outro</option>
                <option value="N">Prefiro não informar</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Tempo na Empresa</label>
              <select
                value={demographics.tempo_empresa}
                onChange={(e) => setDemographics((d) => ({ ...d, tempo_empresa: e.target.value }))}
                className="w-full border border-slate-300 rounded-lg text-sm py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Prefiro não informar</option>
                {['<1', '1-3', '3-5', '5-10', '>10'].map((v) => (
                  <option key={v} value={v}>{v} anos</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="w-full flex items-center justify-center gap-2 bg-blue-700 hover:bg-blue-800 disabled:opacity-60 text-white font-medium py-3 rounded-lg transition-colors"
        >
          {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
          {submitting ? 'Enviando...' : 'Enviar Respostas'}
        </button>
      </div>
    </div>
  )
}
