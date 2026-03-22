import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/services/api'
import toast from 'react-hot-toast'

export function useCompanies() {
  return useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const res = await api.get('/companies/')
      return res.data
    },
  })
}

export function useCompany(id: string) {
  return useQuery({
    queryKey: ['companies', id],
    queryFn: async () => {
      const res = await api.get(`/companies/${id}`)
      return res.data
    },
    enabled: !!id,
  })
}

export function useCreateCompany() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: any) => {
      const res = await api.post('/companies/', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      toast.success('Empresa criada com sucesso')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao criar empresa')
    },
  })
}

export function useUpdateCompany(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: any) => {
      const res = await api.patch(`/companies/${id}`, data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies', id] })
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      toast.success('Empresa atualizada')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Erro ao atualizar empresa')
    },
  })
}
