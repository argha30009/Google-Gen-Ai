import React from 'react';
import { AlertCircleIcon, CheckCircle, XCircle } from 'lucide-react';
import { useNews } from '../context/NewsContext';
export function FactCheckReport() {
  const { newsData, loading } = useNews();

  console.log('📝 FactCheckReport render - loading:', loading, 'hasData:', !!newsData);

  if (loading) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-3">
          Fact Check Report
        </h2>
        <div className="flex items-center gap-3">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          <p className="text-sm text-gray-600">Loading...</p>
        </div>
      </div>;
  }

  if (!newsData) {
    console.log('❌ FactCheckReport: No newsData');
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-3">
          Fact Check Report
        </h2>
        <p className="text-sm text-gray-600">Search for a news topic to see fact check analysis</p>
      </div>;
  }

  const isNoData = newsData.status === 'no_data';
  const factCheck = newsData.summary?.fact_check || '';
  
  console.log('📄 FactCheckReport: factCheck length:', factCheck.length);

  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-3">
        Fact Check Report
      </h2>
      {isNoData ? (
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-400 text-white text-sm font-medium rounded-full">
            <XCircle className="w-4 h-4" />
            No Data
          </span>
          <p className="text-sm text-gray-600">
            {factCheck || 'Could not find any data for the topic'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-3">
            <span className="flex items-center gap-1.5 px-3 py-1.5 bg-orange-500 text-white text-sm font-medium rounded-full">
              <AlertCircleIcon className="w-4 h-4" />
              Analysis Complete
            </span>
            <p className="text-sm text-gray-600">
              Based on {newsData.sentiment_analysis.sentiment_summary.total_analyzed} sources
            </p>
          </div>
          <div className="text-sm text-gray-700 whitespace-pre-line leading-relaxed prose prose-sm max-w-none">
            {factCheck.split('\n').map((paragraph, index) => (
              paragraph.trim() ? <p key={index} className="mb-2">{paragraph}</p> : null
            ))}
          </div>
        </div>
      )}
    </div>;
}