export type RiskLevel = 'aceitavel' | 'moderado' | 'importante' | 'critico'

export interface DashboardMetrics {
  total_invited: number
  total_responded: number
  adhesion_rate: number
  igrp: number
  high_risk_pct: number
}

export interface DimensionScore {
  dimension: string
  dimension_label: string
  score: number
  risk_level: RiskLevel
}

export interface SectorScore {
  sector_nome: string
  unit_nome: string
  pct_critical: number
  response_count: number
  igrp: number
}

export interface RiskDistribution {
  aceitavel: number
  moderado: number
  importante: number
  critico: number
}

export interface HeatmapRow {
  sector_nome: string
  unit_nome: string
  scores: Record<string, number>
}

export interface DemographicDistribution {
  label: string
  count: number
  pct: number
  igrp: number
}

export interface TopCriticalGroup {
  group_type: string
  group_label: string
  igrp: number
  risk_level: RiskLevel
  response_count: number
  top_dimension: string
}

export interface ScoreByGroup {
  group_label: string
  scores: Record<string, number>
  igrp: number
}

export interface DashboardData {
  campaign_id: string
  campaign_nome: string
  metrics: DashboardMetrics
  dimension_scores: DimensionScore[]
  top5_sectors: SectorScore[]
  risk_distribution: RiskDistribution
  demographic_gender: DemographicDistribution[]
  demographic_age: DemographicDistribution[]
  demographic_tenure: DemographicDistribution[]
  heatmap: HeatmapRow[]
  scores_by_gender: ScoreByGroup[]
  scores_by_age: ScoreByGroup[]
  top_critical_groups: TopCriticalGroup[]
}

export interface ReportStatus {
  ready: boolean
  generated_at: string | null
  url: string | null
}
