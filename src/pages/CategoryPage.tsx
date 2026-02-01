import { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Cpu, BarChart3, Rocket, RefreshCw } from 'lucide-react'
import { ArticleCard } from '../components'
import { getArticles, getStats, toggleFavorite } from '../api'
import type { Article, Stats } from '../api'
import type { Category } from '../types'
import { getCategoryInfo, CATEGORIES } from '../types'

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  'tech-innovation': Cpu,
  'benchmarking': BarChart3,
  'product': Rocket,
}

export function CategoryPage() {
  const { categoryId } = useParams<{ categoryId: Category }>()
  const [articles, setArticles] = useState<Article[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState('')

  const categoryInfo = categoryId ? getCategoryInfo(categoryId) : CATEGORIES[0]
  const Icon = iconMap[categoryInfo.id] || Cpu

  // 加载数据
  const loadData = async () => {
    if (!categoryId) return

    setLoading(true)
    setError(null)

    try {
      const [articlesData, statsData] = await Promise.all([
        getArticles({
          category: categoryId,
          date: selectedDate || undefined,
        }),
        getStats(),
      ])

      setArticles(articlesData)
      setStats(statsData)
    } catch (err) {
      console.error('加载数据失败:', err)
      setError('加载数据失败，请检查后端服务是否运行')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [categoryId, selectedDate])

  // 处理收藏
  const handleToggleFavorite = async (id: string) => {
    try {
      const result = await toggleFavorite(id)
      setArticles((prev) =>
        prev.map((a) => (a.id === id ? { ...a, is_favorited: result.is_favorited } : a))
      )
    } catch (err) {
      console.error('收藏失败:', err)
    }
  }

  // 转换文章格式
  const formattedArticles = useMemo(() => {
    return articles.map((a) => ({
      id: a.id,
      title: a.title,
      summary: a.summary || a.original_content || '',
      category: a.category as Category,
      source: a.source,
      sourceUrl: a.source_url,
      publishedAt: a.collected_at.split('T')[0],
      tags: a.tags,
      author: a.author || undefined,
      subCategory: a.sub_category || undefined,
      isFavorited: a.is_favorited,
    }))
  }, [articles])

  return (
    <div className="space-y-8">
      {/* Back Link */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        返回全部
      </Link>

      {/* Category Header */}
      <section className={`rounded-2xl p-8 ${categoryInfo.bgColor} border ${categoryInfo.borderColor}`}>
        <div className="flex items-center gap-4 mb-4">
          <div className={`p-3 rounded-xl bg-gray-900/50`}>
            <Icon className={`w-8 h-8 ${categoryInfo.color}`} />
          </div>
          <div>
            <h1 className={`text-3xl font-bold ${categoryInfo.color}`}>
              {categoryInfo.nameCn}
            </h1>
            <p className="text-gray-400">{categoryInfo.name}</p>
          </div>
        </div>
        <p className="text-gray-300 max-w-2xl">{categoryInfo.description}</p>
      </section>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-4">
        {/* 日期筛选 */}
        {stats && stats.available_dates.length > 0 && (
          <select
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-pulse-primary"
          >
            <option value="">全部日期</option>
            {stats.available_dates.map((date) => (
              <option key={date} value={date}>
                {date}
              </option>
            ))}
          </select>
        )}

        {/* 刷新按钮 */}
        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 text-gray-400 hover:bg-gray-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          刷新
        </button>
      </div>

      {/* Articles */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            {categoryInfo.nameCn}情报
            <span className="text-sm text-gray-500 ml-2">共 {articles.length} 条</span>
          </h2>
        </div>

        {error ? (
          <div className="text-center py-12">
            <p className="text-red-400 mb-4">{error}</p>
            <button onClick={loadData} className="text-pulse-primary hover:underline">
              重试
            </button>
          </div>
        ) : loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-pulse-primary mx-auto mb-4" />
            <p className="text-gray-500">加载中...</p>
          </div>
        ) : formattedArticles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {formattedArticles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                onToggleFavorite={() => handleToggleFavorite(article.id)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <p>该分类暂无情报</p>
            <Link to="/" className="mt-4 inline-block text-pulse-primary hover:underline">
              查看全部情报
            </Link>
          </div>
        )}
      </section>

      {/* Related Categories */}
      <section>
        <h3 className="text-lg font-semibold text-white mb-4">其他分类</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {CATEGORIES.filter((cat) => cat.id !== categoryId).map((cat) => {
            const CatIcon = iconMap[cat.id] || Cpu
            const count = stats?.by_category[cat.id] || 0
            return (
              <Link
                key={cat.id}
                to={`/category/${cat.id}`}
                className="card-gradient rounded-xl p-4 hover:border-gray-600 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <CatIcon className={`w-5 h-5 ${cat.color}`} />
                  <div>
                    <p className={`font-medium ${cat.color}`}>{cat.nameCn}</p>
                    <p className="text-xs text-gray-500">{count} 条情报</p>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      </section>
    </div>
  )
}
