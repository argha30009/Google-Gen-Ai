import React from 'react';
import { useNews } from '../context/NewsContext';
export function HeadlineSummary() {
  const { newsData, loading } = useNews();

  console.log('📰 HeadlineSummary render - loading:', loading, 'hasData:', !!newsData);
  console.log('📰 Headlines:', newsData?.search_results?.headlines?.length);

  if (loading) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          Headline Summary
        </h2>
        <p className="text-sm text-gray-600">Loading headlines...</p>
      </div>;
  }

  if (!newsData || !newsData.search_results?.headlines?.length) {
    console.log('❌ HeadlineSummary: No headlines data', newsData);
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          Headline Summary
        </h2>
        <p className="text-sm text-gray-600">
          {newsData?.status === 'no_data' ? 'Could not find any data for the topic' : 'Search for a news topic to see headlines'}
        </p>
      </div>;
  }

  const headlines = newsData.search_results.headlines.slice(0, 10);
  const sentimentMap = newsData.sentiment_analysis.per_item.reduce((acc, item) => {
    acc[item.headline] = item.sentiment;
    return acc;
  }, {} as Record<string, string>);

  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-4">
        Headline Summary
      </h2>
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {headlines.map((headline, index) => {
          const sentiment = sentimentMap[headline.title] || 'neutral';
          const sentimentColor = sentiment === 'positive' ? 'bg-green-100 text-green-800' : 
                                  sentiment === 'negative' ? 'bg-red-100 text-red-800' : 
                                  'bg-gray-100 text-gray-800';
          
          return <div key={index} className="space-y-2 pb-3 border-b border-gray-100 last:border-b-0">
              <div className="flex items-start gap-2">
                <div className="flex-shrink-0 w-5 h-5 bg-amber-100 text-amber-800 rounded flex items-center justify-center text-xs font-semibold">
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-gray-900 mb-1">
                    {headline.title}
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${sentimentColor} font-medium`}>
                      {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
                    </span>
                  </div>
                </div>
              </div>
            </div>;
        })}
      </div>
    </div>;
}