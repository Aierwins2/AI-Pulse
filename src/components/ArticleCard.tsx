import { ExternalLink, Clock, User, Star } from 'lucide-react'
import type { Category } from '../types'
import { CategoryBadge } from './CategoryBadge'

interface ArticleCardProps {
  article: {
    id: string
    title: string
    summary: string
    category: Category
    source: string
    sourceUrl: string
    publishedAt: string
    tags: string[]
    author?: string
    subCategory?: string
    isFavorited?: boolean
  }
  onToggleFavorite?: () => void
}

const categoryColorMap: Record<Category, string> = {
  'tech-innovation': 'text-blue-400',
  'benchmarking': 'text-emerald-400',
  'product': 'text-amber-400',
}

export function ArticleCard({ article, onToggleFavorite }: ArticleCardProps) {
  const categoryColor = categoryColorMap[article.category] || 'text-gray-400'

  return (
    <article className="card-gradient rounded-xl p-5 hover:border-gray-600 transition-all duration-300 hover:shadow-xl hover:shadow-black/20 group">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-2">
          <CategoryBadge category={article.category} />
          {article.subCategory && (
            <span className="px-2 py-0.5 bg-gray-800 text-gray-400 text-xs rounded-full">
              {article.subCategory}
            </span>
          )}
        </div>
        {onToggleFavorite && (
          <button
            onClick={(e) => {
              e.preventDefault()
              onToggleFavorite()
            }}
            className="p-1 hover:bg-gray-800 rounded transition-colors"
          >
            <Star
              className={`w-4 h-4 transition-colors ${
                article.isFavorited
                  ? 'text-yellow-400 fill-yellow-400'
                  : 'text-gray-500 hover:text-yellow-400'
              }`}
            />
          </button>
        )}
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-pulse-primary transition-colors line-clamp-2">
        {article.title}
      </h3>

      {/* Summary */}
      <p className="text-gray-400 text-sm leading-relaxed mb-4 line-clamp-3">
        {article.summary}
      </p>

      {/* Tags */}
      {article.tags && article.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {article.tags.slice(0, 4).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 bg-gray-800 text-gray-400 text-xs rounded-md hover:bg-gray-700 cursor-pointer transition-colors"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-800">
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {article.publishedAt}
          </span>
          {article.author && (
            <span className="flex items-center gap-1">
              <User className="w-3 h-3" />
              {article.author}
            </span>
          )}
        </div>
        <a
          href={article.sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={`flex items-center gap-1 text-xs ${categoryColor} opacity-70 hover:opacity-100 transition-opacity`}
        >
          {article.source}
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </article>
  )
}
