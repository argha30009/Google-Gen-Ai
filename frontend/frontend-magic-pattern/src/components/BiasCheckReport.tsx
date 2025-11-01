import React from 'react';
import { useNews } from '../context/NewsContext';
export function BiasCheckReport() {
  const { newsData, loading } = useNews();

  if (loading) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-3">
          Bias Check Report
        </h2>
        <p className="text-sm text-gray-600">Loading...</p>
      </div>;
  }

  if (!newsData) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-3">
          Bias Check Report
        </h2>
        <p className="text-sm text-gray-600">Search for a news topic to see bias analysis</p>
      </div>;
  }

  const biasCheck = newsData.summary?.bias_check || 'No bias analysis available';

  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-3">
        Bias Check Report
      </h2>
      <div className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">
        {biasCheck}
      </div>
    </div>;
}