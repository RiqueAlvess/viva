import api from './api'
import { LoginRequest, LoginResponse, RefreshResponse, User } from '@/types/auth.types'

export const authService = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  refresh: async (refreshToken: string): Promise<RefreshResponse> => {
    const response = await api.post<RefreshResponse>('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  logout: async (refreshToken?: string): Promise<void> => {
    await api.post('/auth/logout', { refresh_token: refreshToken || '' })
  },

  me: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },
}
