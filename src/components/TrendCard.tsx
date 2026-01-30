import { TrendingUp, Calendar, Sparkles } from 'lucide-react'
import type { TrendCard as TrendCardType } from '../types'
import { CategoryBadge } from './CategoryBadge'

interface TrendCardProps {
  trend: TrendCardType
}

export function TrendCard({ trend }: TrendCardProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-pulse-primary/20 via-purple-900/20 to-pulse-secondary/20 border border-pulse-primary/30 p-6 md:p-8">
      {/* Background Effect */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-pulse-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-pulse-secondary/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />

      {/* Content */}
      <div className="relative">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-pulse-primary/20 rounded-lg">
            <TrendingUp className="w-6 h-6 text-pulse-primary" />
          </div>
          <div>
            <h2 className="text-xl md:text-2xl font-bold text-white">{trend.title}</h2>
            <div className="flex items-center gap-2 text-sm text-gray-400 mt-1">
              <Calendar className="w-4 h-4" />
              <span>{trend.date}</span>
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-300 mb-6">{trend.description}</p>

        {/* Categories */}
        <div className="flex flex-wrap gap-2 mb-6">
          {trend.categories.map((cat) => (
            <CategoryBadge key={cat} category={cat} />
          ))}
        </div>

        {/* Highlights */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm font-medium text-pulse-primary">
            <Sparkles className="w-4 h-4" />
            <span>今日要点</span>
          </div>
          <ul className="space-y-2">
            {trend.highlights.map((highlight, index) => (
              <li key={index} className="flex items-start gap-3 text-sm text-gray-300">
                <span className="flex-shrink-0 w-5 h-5 bg-gray-800 rounded-full flex items-center justify-center text-xs text-gray-500">
                  {index + 1}
                </span>
                <span>{highlight}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
