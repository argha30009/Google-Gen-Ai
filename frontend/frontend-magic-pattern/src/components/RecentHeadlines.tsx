import React from 'react';
export function RecentHeadlines() {
  const headlines = [{
    number: 1,
    title: 'Major airline to eliminate all domestic baggage fees in 2026',
    source: 'Aviation Daily',
    time: '2h ago',
    status: 'Unverified',
    statusColor: 'bg-yellow-100 text-yellow-800'
  }, {
    number: 2,
    title: 'City approves pilot program for free public transit on weekends',
    source: 'Metro Times',
    time: '1h ago',
    status: 'Likely true',
    statusColor: 'bg-green-500 text-white'
  }, {
    number: 3,
    title: 'Video claims new phone model is waterproof up to 100m',
    source: 'TechNow',
    time: '4h ago',
    status: 'Needs review',
    statusColor: 'bg-orange-500 text-white'
  }, {
    number: 4,
    title: 'Government announces universal basic income rollout next month',
    source: 'Daily Ledger',
    time: '3h ago',
    status: 'Likely false',
    statusColor: 'bg-red-500 text-white'
  }];
  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-gray-900">
          Recent headlines
        </h2>
        <button className="text-xs text-gray-600 hover:text-gray-900">
          View all
        </button>
      </div>
      <div className="space-y-3">
        {headlines.map(headline => <div key={headline.number} className="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0 last:pb-0">
            <div className="flex-shrink-0 w-6 h-6 bg-[#E8DFC8] rounded flex items-center justify-center text-xs font-semibold">
              {headline.number}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-gray-900 mb-1">
                {headline.title}
              </h3>
              <p className="text-xs text-gray-500">
                Source: {headline.source} • {headline.time}
              </p>
            </div>
            <span className={`flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-medium ${headline.statusColor}`}>
              {headline.status}
            </span>
          </div>)}
      </div>
    </div>;
}