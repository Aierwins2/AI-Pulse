export type Category = 'tech-innovation' | 'benchmarking' | 'product' | 'insights'

export interface Article {
  id: string
  title: string
  summary: string
  category: Category
  subCategory?: string
  source: string
  sourceUrl: string
  publishedAt: string
  tags: string[]
  author?: string
  isFavorited?: boolean
  importance?: 'high' | 'medium' | 'low'
}

export interface TrendCard {
  id: string
  title: string
  description: string
  date: string
  highlights: string[]
  categories: Category[]
}

export interface CategoryInfo {
  id: Category
  name: string
  nameCn: string
  description: string
  icon: string
  color: string
  bgColor: string
  borderColor: string
}

export const CATEGORIES: CategoryInfo[] = [
  {
    id: 'tech-innovation',
    name: 'Tech-Innovation',
    nameCn: '技术创新',
    description: '技术创新：模型架构、训练方法、算法改进（LLM、多模态等）',
    icon: 'Cpu',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
    borderColor: 'border-blue-500/30',
  },
  {
    id: 'benchmarking',
    name: 'Benchmarking',
    nameCn: '模型评测',
    description: '模型评测：评估标准、Benchmark、能力测试（代码、GUI等）',
    icon: 'BarChart3',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/20',
    borderColor: 'border-emerald-500/30',
  },
  {
    id: 'product',
    name: 'Product',
    nameCn: '产品动态',
    description: '产品动态：AI公司产品发布、功能更新、商业动态',
    icon: 'Rocket',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/20',
    borderColor: 'border-amber-500/30',
  },
]

export function getCategoryInfo(category: Category): CategoryInfo {
  return CATEGORIES.find(c => c.id === category) || CATEGORIES[0]
}
