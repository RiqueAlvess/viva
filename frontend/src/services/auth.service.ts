import api from './api'
import { LoginRequest, LoginResponse, User } from '@/types/auth.types'

export const authService = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  me: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },
}
