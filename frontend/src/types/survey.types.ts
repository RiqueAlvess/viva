export type Dimension =
  | 'demandas'
  | 'controle'
  | 'apoio_chefia'
  | 'apoio_colegas'
  | 'relacionamentos'
  | 'cargo'
  | 'comunicacao_mudancas'

export interface SurveyQuestion {
  id: number
  dimension: Dimension
  text: string
}

export interface SurveyValidateResponse {
  valid: boolean
  already_responded?: boolean
  company_nome?: string
  campaign_nome?: string
  token?: string
}

export interface DemographicData {
  faixa_etaria?: string
  genero?: string
  tempo_empresa?: string
}

export interface SurveyAnswer {
  question_id: number
  answer: number // 1-5
}

export interface SurveySubmitRequest {
  token: string
  lgpd_consent: boolean
  demographics: DemographicData
  answers: SurveyAnswer[]
}

export interface SurveySubmitResponse {
  success: boolean
  message: string
}

export type SurveyStep = 'loading' | 'invalid' | 'already_responded' | 'consent' | 'demographics' | 'questionnaire' | 'submitted'
