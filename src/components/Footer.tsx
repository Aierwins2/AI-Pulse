import { Activity, Github, Twitter } from 'lucide-react'

export function Footer() {
  return (
    <footer className="bg-gray-900/50 border-t border-gray-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-6 h-6 text-pulse-primary" />
              <span className="text-lg font-bold text-gradient">AI Pulse</span>
            </div>
            <p className="text-gray-400 text-sm max-w-md">
              一站式 AI 行业前沿深度情报扫描与自动化摘要系统。
              解决 AI 从业者在海量信息流中的"信息焦虑"与"筛选成本"。
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">内容分类</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="/category/tech-innovation" className="hover:text-blue-400 transition-colors">技术创新</a></li>
              <li><a href="/category/benchmarking" className="hover:text-emerald-400 transition-colors">评测方法</a></li>
              <li><a href="/category/product" className="hover:text-amber-400 transition-colors">产品动态</a></li>
              <li><a href="/category/insights" className="hover:text-red-400 transition-colors">行业洞察</a></li>
            </ul>
          </div>

          {/* Data Sources */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4">数据来源</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>arXiv</li>
              <li>Hugging Face</li>
              <li>Product Hunt</li>
              <li>X (Twitter)</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-500">
            &copy; 2026 AI Pulse. 每日 09:00 (北京时间) 自动更新
          </p>
          <div className="flex items-center gap-4">
            <a href="#" className="text-gray-500 hover:text-white transition-colors">
              <Github className="w-5 h-5" />
            </a>
            <a href="#" className="text-gray-500 hover:text-white transition-colors">
              <Twitter className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
