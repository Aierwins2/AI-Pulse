import { Cpu, BarChart3, Rocket, Lightbulb } from 'lucide-react'
import type { Category } from '../types'
import { getCategoryInfo } from '../types'

interface CategoryBadgeProps {
  category: Category
  showLabel?: boolean
}

const iconMap = {
  'tech-innovation': Cpu,
  'benchmarking': BarChart3,
  'product': Rocket,
  'insights': Lightbulb,
}

export function CategoryBadge({ category, showLabel = true }: CategoryBadgeProps) {
  const info = getCategoryInfo(category)
  const Icon = iconMap[category]

  return (
    <span className={`category-badge flex items-center gap-1.5 ${info.bgColor} ${info.color} border ${info.borderColor}`}>
      <Icon className="w-3 h-3" />
      {showLabel && <span>{info.nameCn}</span>}
    </span>
  )
}
