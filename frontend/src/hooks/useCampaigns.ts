import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { campaignsService } from '@/services/campaigns.service'
import { CampaignCreateRequest, CampaignUpdateRequest } from '@/types/campaign.types'
import toast from 'react-hot-toast'

export function useCampaigns() {
  return useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsService.list(),
  })
}

export function useCampaign(id: string) {
  return useQuery({
    queryKey: ['campaigns', id],
    queryFn: () => campaignsService.get(id),
    enabled: !!id,
  })
}

export function useCreateCampaign() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CampaignCreateRequest) => campaignsService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('Campanha criada com sucesso')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao criar campanha')
    },
  })
}

export function useUpdateCampaign(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CampaignUpdateRequest) => campaignsService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns', id] })
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('Campanha atualizada')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao atualizar campanha')
    },
  })
}

export function useActivateCampaign() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => campaignsService.activate(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns', id] })
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('Campanha ativada com sucesso')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao ativar campanha')
    },
  })
}

export function useCloseCampaign() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => campaignsService.close(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns', id] })
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('Campanha encerrada')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao encerrar campanha')
    },
  })
}

export function useCampaignHierarchy(id: string) {
  return useQuery({
    queryKey: ['campaigns', id, 'hierarchy'],
    queryFn: () => campaignsService.getHierarchy(id),
    enabled: !!id,
  })
}
