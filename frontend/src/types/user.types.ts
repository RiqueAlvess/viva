import { Role } from './auth.types'

export interface UserProfile {
  id: string
  nome: string
  email: string
  role: Role
  company_id: string | null
  company_nome?: string
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface CreateUserRequest {
  nome: string
  email: string
  password: string
  role: Role
  company_id?: string | null
  ativo?: boolean
}

export interface UpdateUserRequest {
  nome?: string
  email?: string
  password?: string
  role?: Role
  company_id?: string | null
  ativo?: boolean
}

export interface Company {
  id: string
  nome: string
  cnpj?: string
  email?: string
  telefone?: string
  ativo: boolean
  created_at: string
  updated_at: string
  user_count?: number
  campaign_count?: number
}

export interface CreateCompanyRequest {
  nome: string
  cnpj?: string
  email?: string
  telefone?: string
}

export interface UpdateCompanyRequest {
  nome?: string
  cnpj?: string
  email?: string
  telefone?: string
  ativo?: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
