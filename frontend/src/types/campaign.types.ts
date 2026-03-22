export type CampaignStatus = 'draft' | 'active' | 'closed'

export interface Campaign {
  id: string
  nome: string
  descricao: string | null
  data_inicio: string
  data_fim: string
  status: CampaignStatus
  company_id: string
  company_nome?: string
  created_at: string
  updated_at: string
  total_invited?: number
  total_responded?: number
}

export interface CampaignCreateRequest {
  nome: string
  descricao?: string
  data_inicio: string
  data_fim: string
  company_id?: string
}

export interface CampaignUpdateRequest {
  nome?: string
  descricao?: string
  data_inicio?: string
  data_fim?: string
}

export interface Unit {
  id: string
  nome: string
  campaign_id: string
  sectors?: Sector[]
}

export interface Sector {
  id: string
  nome: string
  unit_id: string
  campaign_id: string
  positions?: Position[]
  collaborator_count?: number
}

export interface Position {
  id: string
  nome: string
  sector_id: string
  collaborators?: Collaborator[]
  collaborator_count?: number
}

export interface Collaborator {
  id: string
  email_hash: string
  position_id: string
}

export interface HierarchyData {
  units: Unit[]
  total_units: number
  total_sectors: number
  total_positions: number
  total_collaborators: number
}

export interface Invitation {
  id: string
  hash: string
  campaign_id: string
  collaborator_id: string
  status: 'pending' | 'sent' | 'responded'
  display_status: string
  sent_at: string | null
  responded_at: string | null
  unidade?: string
  setor?: string
}

export interface InvitationStats {
  total: number
  sent: number
  responded: number
  pending: number
}

export interface CSVPreviewData {
  headers: string[]
  rows: string[][]
  total_rows: number
  errors: CSVError[]
  valid_rows: number
}

export interface CSVError {
  row: number
  column: string
  message: string
}

export interface CSVUploadResponse {
  success: boolean
  message: string
  imported: number
  errors: CSVError[]
}
