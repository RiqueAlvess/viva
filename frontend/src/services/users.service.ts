import api from './api'
import { UserProfile, CreateUserRequest, UpdateUserRequest, Company, CreateCompanyRequest, UpdateCompanyRequest, PaginatedResponse } from '@/types/user.types'

export const usersService = {
  list: async (params?: { page?: number; size?: number; company_id?: string }): Promise<PaginatedResponse<UserProfile>> => {
    const response = await api.get<PaginatedResponse<UserProfile>>('/dashboard/users', { params })
    return response.data
  },

  get: async (id: string): Promise<UserProfile> => {
    const response = await api.get<UserProfile>(`/dashboard/users/${id}`)
    return response.data
  },

  create: async (data: CreateUserRequest): Promise<UserProfile> => {
    const response = await api.post<UserProfile>('/dashboard/users', data)
    return response.data
  },

  update: async (id: string, data: UpdateUserRequest): Promise<UserProfile> => {
    const response = await api.put<UserProfile>(`/dashboard/users/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/dashboard/users/${id}`)
  },
}

export const adminUsersService = {
  list: async (params?: { page?: number; size?: number; company_id?: string }): Promise<PaginatedResponse<UserProfile>> => {
    const response = await api.get<PaginatedResponse<UserProfile>>('/admin/users', { params })
    return response.data
  },

  create: async (data: CreateUserRequest): Promise<UserProfile> => {
    const response = await api.post<UserProfile>('/admin/users', data)
    return response.data
  },
}

export const companiesService = {
  list: async (params?: { page?: number; size?: number }): Promise<PaginatedResponse<Company>> => {
    const response = await api.get<PaginatedResponse<Company>>('/admin/companies', { params })
    return response.data
  },

  get: async (id: string): Promise<Company> => {
    const response = await api.get<Company>(`/admin/companies/${id}`)
    return response.data
  },

  create: async (data: CreateCompanyRequest): Promise<Company> => {
    const response = await api.post<Company>('/admin/companies', data)
    return response.data
  },

  update: async (id: string, data: UpdateCompanyRequest): Promise<Company> => {
    const response = await api.put<Company>(`/admin/companies/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/admin/companies/${id}`)
  },
}
