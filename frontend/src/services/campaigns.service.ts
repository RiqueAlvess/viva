import api from './api'
import {
  Campaign,
  CampaignCreateRequest,
  CampaignUpdateRequest,
  HierarchyData,
} from '@/types/campaign.types'

export const campaignsService = {
  list: async (): Promise<Campaign[]> => {
    const response = await api.get<Campaign[]>('/campaigns/')
    return response.data
  },

  get: async (id: string): Promise<Campaign> => {
    const response = await api.get<Campaign>(`/campaigns/${id}`)
    return response.data
  },

  create: async (data: CampaignCreateRequest): Promise<Campaign> => {
    const response = await api.post<Campaign>('/campaigns/', data)
    return response.data
  },

  update: async (id: string, data: CampaignUpdateRequest): Promise<Campaign> => {
    const response = await api.patch<Campaign>(`/campaigns/${id}`, data)
    return response.data
  },

  activate: async (id: string): Promise<Campaign> => {
    const response = await api.post<Campaign>(`/campaigns/${id}/activate`)
    return response.data
  },

  close: async (id: string): Promise<Campaign> => {
    const response = await api.post<Campaign>(`/campaigns/${id}/close`, { confirm: true })
    return response.data
  },

  getHierarchy: async (id: string): Promise<HierarchyData> => {
    const response = await api.get<HierarchyData>(`/campaigns/${id}/hierarchy`)
    return response.data
  },
}
