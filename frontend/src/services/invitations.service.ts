import api from './api'
import { SurveyValidateResponse, SurveySubmitRequest, SurveySubmitResponse } from '@/types/survey.types'

export const surveyService = {
  validate: async (token: string): Promise<SurveyValidateResponse> => {
    const response = await api.get<SurveyValidateResponse>('/survey/validate', { params: { token } })
    return response.data
  },

  submit: async (data: SurveySubmitRequest): Promise<SurveySubmitResponse> => {
    const response = await api.post<SurveySubmitResponse>('/survey/submit', data)
    return response.data
  },
}
