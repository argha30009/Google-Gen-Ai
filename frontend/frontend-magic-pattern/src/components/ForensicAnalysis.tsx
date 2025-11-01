import React from 'react';
import { GlobeIcon, ActivityIcon, TrendingUpIcon } from 'lucide-react';
import { useNews } from '../context/NewsContext';
export function ForensicAnalysis() {
  const { newsData, loading } = useNews();

  if (loading) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          Forensic Analysis
        </h2>
        <p className="text-sm text-gray-600">Loading...</p>
      </div>;
  }

  if (!newsData) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          Forensic Analysis
        </h2>
        <p className="text-sm text-gray-600">Search for a news topic to see forensic analysis</p>
      </div>;
  }

  const forensicAnalysis = newsData.summary?.forensic_analysis || 'No forensic analysis available';
  const totalSources = newsData.sentiment_analysis.sentiment_summary.total_analyzed;

  const metrics = [{
    icon: GlobeIcon,
    label: 'Total Sources',
    value: `${totalSources} headlines`,
    detail: 'analyzed'
  }, {
    icon: ActivityIcon,
    label: 'Sentiment',
    value: newsData.sentiment_analysis.sentiment_summary.overall,
    detail: 'overall tone'
  }, {
    icon: TrendingUpIcon,
    label: 'Coverage',
    value: 'Multiple outlets',
    detail: 'widespread'
  }];

  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-4">
        Forensic Analysis
      </h2>
      <div className="space-y-3 mb-4">
        {metrics.map(metric => <div key={metric.label} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0 w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <metric.icon className="w-4 h-4 text-gray-600" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-xs font-medium text-gray-600 mb-0.5">
                {metric.label}
              </h3>
              <p className="text-sm font-medium text-gray-900 capitalize">
                {metric.value}
              </p>
              {metric.detail && <p className="text-xs text-gray-500">{metric.detail}</p>}
            </div>
          </div>)}
      </div>
      <div className="text-xs text-gray-600 leading-relaxed whitespace-pre-line max-h-48 overflow-y-auto">
        {forensicAnalysis}
      </div>
    </div>;
}