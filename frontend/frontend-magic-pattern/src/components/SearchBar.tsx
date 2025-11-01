import React, { useState } from 'react';
import { SearchIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useNews } from '../context/NewsContext';
export function SearchBar() {
  const navigate = useNavigate();
  const { fetchNews, loading } = useNews();
  const [query, setQuery] = useState('');
  const handleCheck = async () => {
    if (query.trim()) {
      await fetchNews(query);
      navigate('/dashboard');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCheck();
    }
  };

  return <div className="mb-6">
      <div className="relative">
        <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Search for news topics (e.g., AI news, technology updates)..." 
          className="w-full pl-11 pr-24 py-3 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-800 focus:border-transparent" 
          disabled={loading}
        />
        <button 
          onClick={handleCheck} 
          disabled={loading || !query.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 px-4 py-1.5 bg-amber-800 hover:bg-amber-900 text-white text-sm rounded-md transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed">
          {loading ? 'Checking...' : 'Check'}
        </button>
      </div>
      <p className="text-xs text-gray-500 mt-2">
        Tip: Try "AI news", "latest technology updates", or "climate change news"
      </p>
    </div>;
}