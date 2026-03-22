import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('E-mail inválido').min(1, 'E-mail é obrigatório'),
  password: z.string().min(1, 'Senha é obrigatória'),
})

export const campaignSchema = z.object({
  nome: z.string().min(3, 'Nome deve ter pelo menos 3 caracteres').max(120, 'Nome muito longo'),
  descricao: z.string().max(500, 'Descrição muito longa').optional(),
  data_inicio: z.string().min(1, 'Data de início é obrigatória'),
  data_fim: z.string().min(1, 'Data de término é obrigatória'),
  company_id: z.string().optional(),
}).refine(
  (data) => {
    if (!data.data_inicio || !data.data_fim) return true
    return new Date(data.data_fim) >= new Date(data.data_inicio)
  },
  { message: 'Data de término deve ser após a data de início', path: ['data_fim'] }
)

export const companySchema = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres').max(200, 'Nome muito longo'),
  cnpj: z
    .string()
    .optional()
    .refine((val) => {
      if (!val) return true
      return /^\d{14}$/.test(val.replace(/\D/g, ''))
    }, 'CNPJ inválido'),
  email: z.string().email('E-mail inválido').optional().or(z.literal('')),
  telefone: z.string().optional(),
})

export const createUserSchema = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  email: z.string().email('E-mail inválido'),
  password: z.string().min(8, 'Senha deve ter pelo menos 8 caracteres'),
  role: z.enum(['ADM', 'RH', 'LIDERANCA']),
  company_id: z.string().optional().nullable(),
  ativo: z.boolean().optional(),
})

export const updateUserSchema = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres').optional(),
  email: z.string().email('E-mail inválido').optional(),
  password: z.string().min(8, 'Senha deve ter pelo menos 8 caracteres').optional().or(z.literal('')),
  role: z.enum(['ADM', 'RH', 'LIDERANCA']).optional(),
  company_id: z.string().optional().nullable(),
  ativo: z.boolean().optional(),
})

export const profileSchema = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  email: z.string().email('E-mail inválido'),
  password: z.string().min(8, 'Senha deve ter pelo menos 8 caracteres').optional().or(z.literal('')),
})

export type LoginFormData = z.infer<typeof loginSchema>
export type CampaignFormData = z.infer<typeof campaignSchema>
export type CompanyFormData = z.infer<typeof companySchema>
export type CreateUserFormData = z.infer<typeof createUserSchema>
export type UpdateUserFormData = z.infer<typeof updateUserSchema>
export type ProfileFormData = z.infer<typeof profileSchema>
