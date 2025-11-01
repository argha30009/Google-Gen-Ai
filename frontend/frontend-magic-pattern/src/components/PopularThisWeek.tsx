import React from 'react';
export function PopularThisWeek() {
  const items = [{
    number: 1,
    title: 'New study links daily coffee to longer lifespan',
    source: 'Global Health',
    time: '1d ago',
    status: 'Unverified',
    statusColor: 'bg-yellow-100 text-yellow-800'
  }, {
    number: 2,
    title: 'Rare earthquake felt across three states overnight',
    source: 'State News',
    time: '12h ago',
    status: 'Needs review',
    statusColor: 'bg-orange-500 text-white'
  }];
  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-gray-900">
          Popular this week
        </h2>
        <button className="text-xs text-gray-600 hover:text-gray-900">
          View all
        </button>
      </div>
      <div className="space-y-3">
        {items.map(item => <div key={item.number} className="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0 last:pb-0">
            <div className="flex-shrink-0 w-6 h-6 bg-[#E8DFC8] rounded flex items-center justify-center text-xs font-semibold">
              {item.number}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-gray-900 mb-1">
                {item.title}
              </h3>
              <p className="text-xs text-gray-500">
                {item.source} • {item.time}
              </p>
            </div>
            <span className={`flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-medium ${item.statusColor}`}>
              {item.status}
            </span>
          </div>)}
      </div>
    </div>;
}