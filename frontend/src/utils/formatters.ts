import { format, parseISO, formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export const formatDate = (date: string | null | undefined): string => {
  if (!date) return '—'
  try {
    return format(parseISO(date), 'dd/MM/yyyy', { locale: ptBR })
  } catch {
    return '—'
  }
}

export const formatDateTime = (date: string | null | undefined): string => {
  if (!date) return '—'
  try {
    return format(parseISO(date), 'dd/MM/yyyy HH:mm', { locale: ptBR })
  } catch {
    return '—'
  }
}

export const formatRelative = (date: string | null | undefined): string => {
  if (!date) return '—'
  try {
    return formatDistanceToNow(parseISO(date), { locale: ptBR, addSuffix: true })
  } catch {
    return '—'
  }
}

export const formatPercent = (value: number | null | undefined, decimals = 1): string => {
  if (value == null) return '—'
  return `${value.toFixed(decimals)}%`
}

export const formatScore = (value: number | null | undefined, decimals = 2): string => {
  if (value == null) return '—'
  return value.toFixed(decimals)
}

export const formatNumber = (value: number | null | undefined): string => {
  if (value == null) return '—'
  return new Intl.NumberFormat('pt-BR').format(value)
}

export const truncateHash = (hash: string, chars = 8): string => {
  if (!hash) return '—'
  return `${hash.slice(0, chars)}...`
}

export const formatCNPJ = (cnpj: string | null | undefined): string => {
  if (!cnpj) return '—'
  const digits = cnpj.replace(/\D/g, '')
  if (digits.length !== 14) return cnpj
  return digits.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
}

export const maskEmail = (email: string): string => {
  const [local, domain] = email.split('@')
  if (!domain) return email
  const masked = local.length > 2 ? `${local[0]}${'*'.repeat(local.length - 2)}${local[local.length - 1]}` : local
  return `${masked}@${domain}`
}
