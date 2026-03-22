import { dashboardService } from './dashboard.service'

export const reportsService = {
  downloadPGR: async (campaignId: string, campaignNome: string): Promise<void> => {
    const blob = await dashboardService.exportPGR(campaignId)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `PGR_${campaignNome.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },
}
