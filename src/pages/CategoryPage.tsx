import { useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Cpu, BarChart3, Rocket, Lightbulb } from 'lucide-react'
import { ArticleCard, FilterBar } from '../components'
import { mockArticles } from '../data/mockData'
import type { Category } from '../types'
import { getCategoryInfo, CATEGORIES } from '../types'

const iconMap = {
  'tech-innovation': Cpu,
  'benchmarking': BarChart3,
  'product': Rocket,
  'insights': Lightbulb,
}

export function CategoryPage() {
  const { categoryId } = useParams<{ categoryId: Category }>()
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'date' | 'importance'>('date')
  const [selectedDate, setSelectedDate] = useState('')

  const categoryInfo = categoryId ? getCategoryInfo(categoryId) : CATEGORIES[0]
  const Icon = iconMap[categoryInfo.id]

  const filteredArticles = useMemo(() => {
    let articles = mockArticles.filter((article) => article.category === categoryId)

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
  }, [categoryId, searchQuery, sortBy, selectedDate])

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
      <FilterBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedCategory={categoryId || 'all'}
        onCategoryChange={() => {}}
        sortBy={sortBy}
        onSortChange={setSortBy}
        selectedDate={selectedDate}
        onDateChange={setSelectedDate}
      />

      {/* Articles */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            {categoryInfo.nameCn}情报
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
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {CATEGORIES.filter((cat) => cat.id !== categoryId).map((cat) => {
            const CatIcon = iconMap[cat.id]
            const count = mockArticles.filter((a) => a.category === cat.id).length
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
