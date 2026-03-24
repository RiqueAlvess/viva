import { useMutation } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/auth.service'
import { LoginRequest } from '@/types/auth.types'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'

export function useLogin() {
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (response) => {
      setAuth(response.user, response.access_token)
      toast.success(`Bem-vindo, ${response.user.nome}!`)
      navigate('/dashboard')
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail
      let message = 'Erro ao fazer login'
      if (typeof detail === 'string') {
        message = detail
      } else if (Array.isArray(detail)) {
        message = detail.map((d: any) => d.msg || String(d)).join(', ')
      }
      toast.error(message)
    },
  })
}

export function useLogout() {
  const { clearAuth } = useAuthStore()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async () => {},
    onSettled: () => {
      clearAuth()
      navigate('/login')
    },
  })
}
