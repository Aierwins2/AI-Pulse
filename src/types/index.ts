export type Category = 'tech-innovation' | 'benchmarking' | 'product' | 'insights'

export interface Article {
  id: string
  title: string
  summary: string
  category: Category
  source: string
  sourceUrl: string
  publishedAt: string
  tags: string[]
  importance: 'high' | 'medium' | 'low'
  author?: string
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
    description: '论文-技术创新：侧重模型架构、训练算力、算法改进',
    icon: 'Cpu',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
    borderColor: 'border-blue-500/30',
  },
  {
    id: 'benchmarking',
    name: 'Benchmarking',
    nameCn: '评测方法',
    description: '论文-评测方法：侧重评估标准、Leaderboard 更新、安全性测试',
    icon: 'BarChart3',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/20',
    borderColor: 'border-emerald-500/30',
  },
  {
    id: 'product',
    name: 'Product',
    nameCn: '产品动态',
    description: '产品与新功能：侧重 C 端应用、API 更新、大厂动作',
    icon: 'Rocket',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/20',
    borderColor: 'border-amber-500/30',
  },
  {
    id: 'insights',
    name: 'Insights',
    nameCn: '行业洞察',
    description: '行业洞察：侧重专家观点、政策趋势、商业逻辑',
    icon: 'Lightbulb',
    color: 'text-red-400',
    bgColor: 'bg-red-500/20',
    borderColor: 'border-red-500/30',
  },
]

export function getCategoryInfo(category: Category): CategoryInfo {
  return CATEGORIES.find(c => c.id === category) || CATEGORIES[0]
}
