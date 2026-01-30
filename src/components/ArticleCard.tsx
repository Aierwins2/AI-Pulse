import { ExternalLink, Clock, User } from 'lucide-react'
import type { Article } from '../types'
import { getCategoryInfo } from '../types'
import { CategoryBadge } from './CategoryBadge'

interface ArticleCardProps {
  article: Article
}

export function ArticleCard({ article }: ArticleCardProps) {
  const categoryInfo = getCategoryInfo(article.category)

  const importanceStyles = {
    high: 'border-l-4 border-l-pulse-primary',
    medium: 'border-l-4 border-l-gray-600',
    low: '',
  }

  return (
    <article
      className={`card-gradient rounded-xl p-5 hover:border-gray-600 transition-all duration-300 hover:shadow-xl hover:shadow-black/20 group ${importanceStyles[article.importance]}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <CategoryBadge category={article.category} />
        {article.importance === 'high' && (
          <span className="px-2 py-0.5 bg-pulse-primary/20 text-pulse-primary text-xs rounded-full">
            重要
          </span>
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
          className={`flex items-center gap-1 text-xs ${categoryInfo.color} opacity-70 hover:opacity-100 transition-opacity`}
        >
          {article.source}
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </article>
  )
}
