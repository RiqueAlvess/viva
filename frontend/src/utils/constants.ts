import { Dimension } from '@/types/survey.types'

export const DIMENSION_COLORS: Record<string, string> = {
  demandas: '#EF4444',
  controle: '#3B82F6',
  apoio_chefia: '#10B981',
  apoio_colegas: '#06B6D4',
  relacionamentos: '#F59E0B',
  cargo: '#8B5CF6',
  comunicacao_mudancas: '#EC4899',
}

export const RISK_COLORS: Record<string, string> = {
  aceitavel: '#10B981',
  moderado: '#F59E0B',
  importante: '#F97316',
  critico: '#EF4444',
}

export const DIMENSION_LABELS: Record<string, string> = {
  demandas: 'Demandas',
  controle: 'Controle',
  apoio_chefia: 'Apoio da Chefia',
  apoio_colegas: 'Apoio dos Colegas',
  relacionamentos: 'Relacionamentos',
  cargo: 'Cargo/Função',
  comunicacao_mudancas: 'Comunicação e Mudanças',
}

export const RISK_LABELS: Record<string, string> = {
  aceitavel: 'Aceitável',
  moderado: 'Moderado',
  importante: 'Importante',
  critico: 'Crítico',
}

export const CAMPAIGN_STATUS_LABELS: Record<string, string> = {
  draft: 'Rascunho',
  active: 'Ativo',
  closed: 'Encerrado',
}

export const ROLE_LABELS: Record<string, string> = {
  ADM: 'Administrador',
  RH: 'RH',
  LIDERANCA: 'Liderança',
}

export const FAIXA_ETARIA_OPTIONS = [
  { value: '18-24', label: '18 a 24 anos' },
  { value: '25-34', label: '25 a 34 anos' },
  { value: '35-44', label: '35 a 44 anos' },
  { value: '45-54', label: '45 a 54 anos' },
  { value: '55+', label: '55 anos ou mais' },
]

export const GENERO_OPTIONS = [
  { value: 'masculino', label: 'Masculino' },
  { value: 'feminino', label: 'Feminino' },
  { value: 'nao_binario', label: 'Não-binário' },
  { value: 'prefiro_nao_dizer', label: 'Prefiro não dizer' },
]

export const TEMPO_EMPRESA_OPTIONS = [
  { value: 'menos_1', label: 'Menos de 1 ano' },
  { value: '1-3', label: '1 a 3 anos' },
  { value: '3-5', label: '3 a 5 anos' },
  { value: '5-10', label: '5 a 10 anos' },
  { value: 'mais_10', label: 'Mais de 10 anos' },
]

export const SURVEY_SCALE_LABELS: Record<number, string> = {
  1: 'Nunca',
  2: 'Raramente',
  3: 'Às vezes',
  4: 'Frequentemente',
  5: 'Sempre',
}

interface SurveyQuestionDef {
  id: number
  dimension: Dimension
  text: string
}

export const SURVEY_QUESTIONS: SurveyQuestionDef[] = [
  { id: 1, dimension: 'cargo', text: 'Eu sei exatamente o que é esperado de mim no trabalho' },
  { id: 2, dimension: 'controle', text: 'Posso decidir quando fazer uma pausa' },
  { id: 3, dimension: 'demandas', text: 'Diferentes grupos no trabalho exigem coisas de mim que são difíceis de combinar' },
  { id: 4, dimension: 'cargo', text: 'Eu sei como fazer meu trabalho' },
  { id: 5, dimension: 'relacionamentos', text: 'Estou sujeito a atenção pessoal ou assédio na forma de palavras ou comportamentos ofensivos' },
  { id: 6, dimension: 'demandas', text: 'Tenho prazos inatingíveis' },
  { id: 7, dimension: 'apoio_colegas', text: 'Se o trabalho fica difícil, meus colegas me ajudam' },
  { id: 8, dimension: 'apoio_chefia', text: 'Sou apoiado(a) em uma crise emocional no trabalho' },
  { id: 9, dimension: 'demandas', text: 'Tenho que trabalhar muito intensamente' },
  { id: 10, dimension: 'controle', text: 'Tenho voz nas mudanças no modo como faço meu trabalho' },
  { id: 11, dimension: 'cargo', text: 'Tenho tempo suficiente para completar meu trabalho' },
  { id: 12, dimension: 'demandas', text: 'Tenho que desconsiderar regras ou procedimentos para fazer o trabalho' },
  { id: 13, dimension: 'cargo', text: 'Sei qual é o meu papel e responsabilidades' },
  { id: 14, dimension: 'relacionamentos', text: 'Tenho que trabalhar com pessoas que têm valores de trabalho diferentes' },
  { id: 15, dimension: 'controle', text: 'Posso planejar quando fazer as pausas' },
  { id: 16, dimension: 'demandas', text: 'Tenho volume de trabalho pesado' },
  { id: 17, dimension: 'cargo', text: 'Existe uma boa combinação entre o que a organização espera de mim e as habilidades que tenho' },
  { id: 18, dimension: 'demandas', text: 'Tenho que trabalhar muito rapidamente' },
  { id: 19, dimension: 'controle', text: 'Tenho uma palavra a dizer sobre o ritmo em que trabalho' },
  { id: 20, dimension: 'demandas', text: 'Tenho que negligenciar alguns aspectos do meu trabalho porque tenho muito a fazer' },
  { id: 21, dimension: 'relacionamentos', text: 'Existe fricção ou raiva entre colegas' },
  { id: 22, dimension: 'demandas', text: 'Não tenho tempo para fazer uma pausa' },
  { id: 23, dimension: 'apoio_chefia', text: 'Minha chefia imediata me encoraja no trabalho' },
  { id: 24, dimension: 'apoio_colegas', text: 'Recebo o respeito no trabalho que mereço de meus colegas' },
  { id: 25, dimension: 'controle', text: 'Tenho controle sobre quando fazer uma pausa' },
  { id: 26, dimension: 'comunicacao_mudancas', text: 'Os funcionários são sempre consultados sobre mudanças no trabalho' },
  { id: 27, dimension: 'apoio_colegas', text: 'Posso contar com meus colegas para me ajudar quando as coisas ficam difíceis no trabalho' },
  { id: 28, dimension: 'comunicacao_mudancas', text: 'Posso conversar com minha chefia sobre algo que me incomodou' },
  { id: 29, dimension: 'apoio_chefia', text: 'Minha chefia me apoia para o trabalho' },
  { id: 30, dimension: 'controle', text: 'Tenho alguma participação em decisões sobre o meu trabalho' },
  { id: 31, dimension: 'apoio_colegas', text: 'Recebo ajuda e apoio de meus colegas' },
  { id: 32, dimension: 'comunicacao_mudancas', text: 'Quando ocorrem mudanças no trabalho, tenho clareza sobre como funcionará na prática' },
  { id: 33, dimension: 'apoio_chefia', text: 'Recebo feedback sobre o meu trabalho' },
  { id: 34, dimension: 'relacionamentos', text: 'Existe tensão entre mim e colegas de trabalho' },
  { id: 35, dimension: 'apoio_chefia', text: 'Minha chefia me incentiva nas minhas atividades' },
]

export const PAGE_SIZE_OPTIONS = [10, 25, 50, 100]
export const DEFAULT_PAGE_SIZE = 25
