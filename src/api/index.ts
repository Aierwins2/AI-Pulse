/**
 * API 服务模块 - 与后端通信
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// 文章类型
export interface Article {
  id: string
  title: string
  summary: string | null
  original_content: string | null
  category: string
  sub_category: string | null
  source: string
  source_url: string
  author: string | null
  tags: string[]
  published_at: string | null
  collected_at: string
  is_favorited: boolean
}

// 趋势总结类型
export interface TrendSummary {
  date: string
  title: string
  summary: string
  highlights: string[]
  article_count: number
}

// 统计信息类型
export interface Stats {
  total: number
  by_category: Record<string, number>
  today: number
  available_dates: string[]
}

// 分类信息类型
export interface CategoryInfo {
  name: string
  description: string
  sub_categories: string[]
}

// API 请求封装
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

// ============ API 方法 ============

/**
 * 获取文章列表
 */
export async function getArticles(params?: {
  category?: string
  date?: string
  favorites?: boolean
  limit?: number
  offset?: number
}): Promise<Article[]> {
  const searchParams = new URLSearchParams()

  if (params?.category) searchParams.set('category', params.category)
  if (params?.date) searchParams.set('date', params.date)
  if (params?.favorites) searchParams.set('favorites', 'true')
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.offset) searchParams.set('offset', params.offset.toString())

  const query = searchParams.toString()
  return fetchAPI<Article[]>(`/api/articles${query ? `?${query}` : ''}`)
}

/**
 * 获取单篇文章
 */
export async function getArticle(id: string): Promise<Article> {
  return fetchAPI<Article>(`/api/articles/${id}`)
}

/**
 * 切换收藏状态
 */
export async function toggleFavorite(id: string): Promise<{ id: string; is_favorited: boolean }> {
  return fetchAPI(`/api/articles/${id}/favorite`, { method: 'POST' })
}

/**
 * 获取趋势总结
 */
export async function getTrend(date?: string): Promise<TrendSummary | null> {
  const query = date ? `?date=${date}` : ''
  return fetchAPI<TrendSummary | null>(`/api/trend${query}`)
}

/**
 * 获取统计信息
 */
export async function getStats(): Promise<Stats> {
  return fetchAPI<Stats>('/api/stats')
}

/**
 * 获取分类列表
 */
export async function getCategories(): Promise<Record<string, CategoryInfo>> {
  return fetchAPI<Record<string, CategoryInfo>>('/api/categories')
}

/**
 * 手动触发爬取
 */
export async function triggerCrawl(): Promise<{ status: string; message: string }> {
  return fetchAPI('/api/crawl', { method: 'POST' })
}
