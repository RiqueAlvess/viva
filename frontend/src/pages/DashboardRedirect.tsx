import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { campaignsService } from '@/services/campaigns.service'
import { useAuthStore } from '@/store/authStore'

export default function DashboardRedirect() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)

  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsService.list(),
  })

  useEffect(() => {
    if (isLoading) return
    if (user?.role === 'ADM') {
      navigate('/dashboard/admin', { replace: true })
      return
    }
    if (campaigns && campaigns.length > 0) {
      navigate(`/dashboard/campaigns/${campaigns[0].id}`, { replace: true })
    } else {
      navigate('/dashboard/campaigns', { replace: true })
    }
  }, [campaigns, isLoading, navigate, user])

  return (
    <div className="flex items-center justify-center h-full">
      <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
    </div>
  )
}
