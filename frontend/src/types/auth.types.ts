export type Role = 'ADM' | 'RH' | 'LIDERANCA'

export interface User {
  id: string
  nome: string
  email: string
  role: Role
  company_id: string | null
  company_nome?: string
  ativo: boolean
  created_at?: string
  updated_at?: string
}

export interface AuthState {
  user: User | null
  access_token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}
