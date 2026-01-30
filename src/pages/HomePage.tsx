import { useState, useMemo } from 'react'
import { Cpu, BarChart3, Rocket, Lightbulb, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { ArticleCard, TrendCard, FilterBar } from '../components'
import { mockArticles, mockTrendCard } from '../data/mockData'
import type { Category } from '../types'
import { CATEGORIES } from '../types'

const iconMap = {
  'tech-innovation': Cpu,
  'benchmarking': BarChart3,
  'product': Rocket,
  'insights': Lightbulb,
}

export function HomePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<Category | 'all'>('all')
  const [sortBy, setSortBy] = useState<'date' | 'importance'>('date')
  const [selectedDate, setSelectedDate] = useState('')

  const filteredArticles = useMemo(() => {
    let articles = [...mockArticles]

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      articles = articles.filter(
        (article) =>
          article.title.toLowerCase().includes(query) ||
          article.summary.toLowerCase().includes(query) ||
          article.tags.some((tag) => tag.toLowerCase().includes(query))
      )
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      articles = articles.filter((article) => article.category === selectedCategory)
    }

    // Filter by date
    if (selectedDate) {
      articles = articles.filter((article) => article.publishedAt === selectedDate)
    }

    // Sort
    if (sortBy === 'importance') {
      const importanceOrder = { high: 0, medium: 1, low: 2 }
      articles.sort((a, b) => importanceOrder[a.importance] - importanceOrder[b.importance])
    } else {
      articles.sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime())
    }

    return articles
  }, [searchQuery, selectedCategory, sortBy, selectedDate])

  // Stats by category
  const categoryStats = useMemo(() => {
    return CATEGORIES.map((cat) => ({
      ...cat,
      count: mockArticles.filter((a) => a.category === cat.id).length,
    }))
  }, [])

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
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {categoryStats.map((cat) => {
          const Icon = iconMap[cat.id]
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
      <section>
        <TrendCard trend={mockTrendCard} />
      </section>

      {/* Filter Bar */}
      <section>
        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          sortBy={sortBy}
          onSortChange={setSortBy}
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
        />
      </section>

      {/* Articles Grid */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            最新情报
            <span className="text-sm text-gray-500 ml-2">
              共 {filteredArticles.length} 条
            </span>
          </h2>
        </div>

        {filteredArticles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredArticles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <p>没有找到匹配的情报</p>
            <button
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory('all')
                setSelectedDate('')
              }}
              className="mt-4 text-pulse-primary hover:underline"
            >
              清除筛选条件
            </button>
          </div>
        )}
      </section>
    </div>
  )
}
