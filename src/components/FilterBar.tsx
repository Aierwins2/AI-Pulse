import { Search, Filter, SortAsc, Calendar } from 'lucide-react'
import type { Category } from '../types'
import { CATEGORIES } from '../types'

interface FilterBarProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  selectedCategory: Category | 'all'
  onCategoryChange: (category: Category | 'all') => void
  sortBy: 'date' | 'importance'
  onSortChange: (sort: 'date' | 'importance') => void
  selectedDate: string
  onDateChange: (date: string) => void
}

export function FilterBar({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  sortBy,
  onSortChange,
  selectedDate,
  onDateChange,
}: FilterBarProps) {
  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 p-4 space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
        <input
          type="text"
          placeholder="搜索标题、摘要或标签..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-pulse-primary focus:ring-1 focus:ring-pulse-primary transition-colors"
        />
      </div>

      {/* Filters Row */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Category Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <select
            value={selectedCategory}
            onChange={(e) => onCategoryChange(e.target.value as Category | 'all')}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-pulse-primary cursor-pointer"
          >
            <option value="all">全部分类</option>
            {CATEGORIES.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.nameCn}
              </option>
            ))}
          </select>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <SortAsc className="w-4 h-4 text-gray-500" />
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value as 'date' | 'importance')}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-pulse-primary cursor-pointer"
          >
            <option value="date">按日期</option>
            <option value="importance">按重要性</option>
          </select>
        </div>

        {/* Date Filter */}
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-gray-500" />
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => onDateChange(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-pulse-primary cursor-pointer"
          />
        </div>

        {/* Clear Filters */}
        {(searchQuery || selectedCategory !== 'all' || selectedDate) && (
          <button
            onClick={() => {
              onSearchChange('')
              onCategoryChange('all')
              onDateChange('')
            }}
            className="px-3 py-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            清除筛选
          </button>
        )}
      </div>
    </div>
  )
}
