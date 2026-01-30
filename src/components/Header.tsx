import { Activity, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { CATEGORIES } from '../types'

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const location = useLocation()

  return (
    <header className="sticky top-0 z-50 bg-gray-950/80 backdrop-blur-lg border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative">
              <Activity className="w-8 h-8 text-pulse-primary group-hover:scale-110 transition-transform" />
              <div className="absolute inset-0 bg-pulse-primary/30 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">AI Pulse</h1>
              <p className="text-xs text-gray-500 -mt-1">AI 脉动</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === '/'
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              全部
            </Link>
            {CATEGORIES.map((cat) => (
              <Link
                key={cat.id}
                to={`/category/${cat.id}`}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  location.pathname === `/category/${cat.id}`
                    ? `${cat.bgColor} ${cat.color}`
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                }`}
              >
                {cat.nameCn}
              </Link>
            ))}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 text-gray-400 hover:text-white"
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <nav className="md:hidden py-4 border-t border-gray-800">
            <Link
              to="/"
              onClick={() => setIsMenuOpen(false)}
              className="block px-4 py-3 text-gray-300 hover:bg-gray-800 rounded-lg"
            >
              全部情报
            </Link>
            {CATEGORIES.map((cat) => (
              <Link
                key={cat.id}
                to={`/category/${cat.id}`}
                onClick={() => setIsMenuOpen(false)}
                className={`block px-4 py-3 rounded-lg ${cat.color} hover:${cat.bgColor}`}
              >
                {cat.nameCn} - {cat.name}
              </Link>
            ))}
          </nav>
        )}
      </div>
    </header>
  )
}
