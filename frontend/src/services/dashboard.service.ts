import api from './api'
import { DashboardData, ReportStatus } from '@/types/dashboard.types'

export const dashboardService = {
  getData: async (campaignId: string): Promise<DashboardData> => {
    const response = await api.get<DashboardData>(`/dashboard/${campaignId}`)
    return response.data
  },

  getReportStatus: async (campaignId: string): Promise<ReportStatus> => {
    const response = await api.get<ReportStatus>(`/dashboard/${campaignId}/report-status`)
    return response.data
  },

  exportPGR: async (campaignId: string): Promise<Blob> => {
    const response = await api.get(`/dashboard/${campaignId}/export-pgr`, {
      responseType: 'blob',
    })
    return response.data
  },
}
