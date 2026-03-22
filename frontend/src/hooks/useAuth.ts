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
      setAuth(response.user, response.access_token, response.refresh_token)
      toast.success(`Bem-vindo, ${response.user.nome}!`)
      navigate('/dashboard')
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Erro ao fazer login'
      toast.error(message)
    },
  })
}

export function useLogout() {
  const { clearAuth, refreshToken } = useAuthStore()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async () => {
      if (refreshToken) {
        await authService.logout(refreshToken)
      }
    },
    onSettled: () => {
      clearAuth()
      navigate('/login')
    },
  })
}
