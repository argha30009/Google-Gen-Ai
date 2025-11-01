import React from 'react';
import { SearchIcon } from 'lucide-react';
export function DashboardHeader() {
  return <div className="mb-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">
        Verify news with confidence
      </h1>
      <div className="relative">
        <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input type="text" placeholder="Search or paste a claim to fact-check (text, image, video...)" className="w-full pl-11 pr-24 py-3 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-800 focus:border-transparent" />
        <button className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 px-4 py-1.5 bg-amber-800 hover:bg-amber-900 text-white text-sm rounded-md transition-colors">
          Check
        </button>
      </div>
      <p className="text-xs text-gray-500 mt-2">
        Tip: Try "Did the city council approve a new congestion tax this week?"
      </p>
    </div>;
}