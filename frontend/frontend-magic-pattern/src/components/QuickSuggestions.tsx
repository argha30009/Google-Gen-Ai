import React from 'react';
export function QuickSuggestions() {
  const suggestions = ['Is this video edited?', 'Source credibility', 'Election claim', 'Health misinformation', 'Climate report', 'Economic stats'];
  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-4">
        Quick suggestions
      </h2>
      <div className="flex flex-wrap gap-2">
        {suggestions.map(suggestion => <button key={suggestion} className="px-3 py-1.5 bg-[#E8DFC8] hover:bg-[#DFD3BA] text-gray-800 text-xs rounded-full transition-colors">
            {suggestion}
          </button>)}
      </div>
    </div>;
}