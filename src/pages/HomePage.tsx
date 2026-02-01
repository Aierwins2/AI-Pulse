import { useState, useEffect, useMemo } from 'react'
import { Cpu, BarChart3, Rocket, ArrowRight, RefreshCw, Star } from 'lucide-react'
import { Link } from 'react-router-dom'
import { ArticleCard, TrendCard } from '../components'
import { getArticles, getStats, getTrend, toggleFavorite } from '../api'
import type { Article, TrendSummary, Stats } from '../api'
import type { Category } from '../types'

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  'tech-innovation': Cpu,
  'benchmarking': BarChart3,
  'product': Rocket,
}

const categoryInfo: Record<string, { nameCn: string; name: string; color: string; bgColor: string }> = {
  'tech-innovation': {
    nameCn: '技术创新',
    name: 'Tech Innovation',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
  },
  'benchmarking': {
    nameCn: '模型评测',
    name: 'Benchmarking',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/20',
  },
  'product': {
    nameCn: '产品动态',
    name: 'Product',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/20',
  },
}

export function HomePage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [trend, setTrend] = useState<TrendSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [selectedCategory, setSelectedCategory] = useState<Category | 'all'>('all')
  const [selectedDate, setSelectedDate] = useState('')
  const [showFavorites, setShowFavorites] = useState(false)

  // 加载数据
  const loadData = async () => {
    setLoading(true)
    setError(null)

    try {
      const [articlesData, statsData, trendData] = await Promise.all([
        getArticles({
          category: selectedCategory !== 'all' ? selectedCategory : undefined,
          date: selectedDate || undefined,
          favorites: showFavorites || undefined,
        }),
        getStats(),
        getTrend(),
      ])

      setArticles(articlesData)
      setStats(statsData)
      setTrend(trendData)
    } catch (err) {
      console.error('加载数据失败:', err)
      setError('加载数据失败，请检查后端服务是否运行')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [selectedCategory, selectedDate, showFavorites])

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

  // 分类统计
  const categoryStats = useMemo(() => {
    if (!stats) return []

    return Object.entries(categoryInfo).map(([id, info]) => ({
      id,
      ...info,
      count: stats.by_category[id] || 0,
    }))
  }, [stats])

  // 转换文章格式以适配 ArticleCard 组件
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

  // 转换趋势格式
  const formattedTrend = useMemo(() => {
    if (!trend) return null
    return {
      id: `trend-${trend.date}`,
      title: trend.title,
      description: trend.summary,
      date: trend.date,
      highlights: trend.highlights,
      categories: Object.keys(categoryInfo) as Category[],
    }
  }, [trend])

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="text-center py-12">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          <span className="text-gradient">AI Pulse</span>
          <span className="text-white"> - AI 脉动</span>
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          一站式 AI 行业前沿深度情报扫描与自动化摘要系统
          <br />
          <span className="text-sm">将碎片化原始信息转化为结构化深度情报</span>
        </p>
      </section>

      {/* Category Stats */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {categoryStats.map((cat) => {
          const Icon = iconMap[cat.id] || Cpu
          return (
            <Link
              key={cat.id}
              to={`/category/${cat.id}`}
              className={`card-gradient rounded-xl p-4 hover:border-gray-600 transition-all group`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className={`p-2 rounded-lg ${cat.bgColor}`}>
                  <Icon className={`w-5 h-5 ${cat.color}`} />
                </div>
                <span className="text-2xl font-bold text-white">{cat.count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`font-medium ${cat.color}`}>{cat.nameCn}</p>
                  <p className="text-xs text-gray-500">{cat.name}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors" />
              </div>
            </Link>
          )
        })}
      </section>

      {/* Trend Card */}
      {formattedTrend && (
        <section>
          <TrendCard trend={formattedTrend} />
        </section>
      )}

      {/* Filter Bar */}
      <section>
        <div className="flex flex-wrap items-center gap-4 mb-4">
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

          {/* 分类筛选 */}
          <div className="flex gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-pulse-primary text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              全部
            </button>
            {Object.entries(categoryInfo).map(([id, info]) => (
              <button
                key={id}
                onClick={() => setSelectedCategory(id as Category)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedCategory === id
                    ? `${info.bgColor} ${info.color}`
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {info.nameCn}
              </button>
            ))}
          </div>

          {/* 收藏筛选 */}
          <button
            onClick={() => setShowFavorites(!showFavorites)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              showFavorites
                ? 'bg-yellow-500/20 text-yellow-400'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <Star className={`w-4 h-4 ${showFavorites ? 'fill-current' : ''}`} />
            收藏夹
          </button>

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
      </section>

      {/* Articles Grid */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            {showFavorites ? '我的收藏' : '最新情报'}
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
            <p>暂无数据</p>
            <p className="text-sm mt-2">请等待每日自动采集或手动触发采集</p>
          </div>
        )}
      </section>
    </div>
  )
}
