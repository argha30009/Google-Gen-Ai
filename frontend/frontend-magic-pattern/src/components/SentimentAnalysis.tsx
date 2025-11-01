import React from 'react';
import { useNews } from '../context/NewsContext';
export function SentimentAnalysis() {
  const { newsData, loading } = useNews();

  if (loading) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          Sentiment Analysis
        </h2>
        <p className="text-sm text-gray-600">Loading...</p>
      </div>;
  }

  if (!newsData) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          Sentiment Analysis
        </h2>
        <p className="text-sm text-gray-600">Search for a news topic to see sentiment analysis</p>
      </div>;
  }

  const { positive_count = 0, negative_count = 0, neutral_count = 0, total_analyzed = 0 } = 
    newsData.sentiment_analysis.sentiment_summary;

  const sentiments = [
    {
      label: 'Positive',
      value: total_analyzed > 0 ? positive_count / total_analyzed : 0,
      count: positive_count,
      color: 'bg-green-500'
    },
    {
      label: 'Negative',
      value: total_analyzed > 0 ? negative_count / total_analyzed : 0,
      count: negative_count,
      color: 'bg-red-500'
    },
    {
      label: 'Neutral',
      value: total_analyzed > 0 ? neutral_count / total_analyzed : 0,
      count: neutral_count,
      color: 'bg-gray-400'
    }
  ];

  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-4">
        Sentiment Analysis
      </h2>
      {total_analyzed > 0 ? (
        <div className="space-y-3">
          {sentiments.map(sentiment => <div key={sentiment.label}>
              <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>{sentiment.label}</span>
                <span>{sentiment.count} ({(sentiment.value * 100).toFixed(0)}%)</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div className={`${sentiment.color} h-full rounded-full transition-all`} style={{
              width: `${sentiment.value * 100}%`
            }} />
              </div>
            </div>)}
        </div>
      ) : (
        <p className="text-sm text-gray-600">No sentiment data available</p>
      )}
    </div>;
}