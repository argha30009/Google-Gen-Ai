import React from 'react';
import { DashboardHeader } from '../components/DashboardHeader';
import { FactCheckReport } from '../components/FactCheckReport';
import { HeadlineSummary } from '../components/HeadlineSummary';
import { SentimentAnalysis } from '../components/SentimentAnalysis';
import { ForensicAnalysis } from '../components/ForensicAnalysis';
import { BiasCheckReport } from '../components/BiasCheckReport';
import { UpcomingFeatures } from '../components/UpcomingFeatures';
import { useNews } from '../context/NewsContext';
export function Dashboard() {
  const { error, newsData } = useNews();

  console.log('📊 Dashboard render - error:', error, 'hasData:', !!newsData);

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  return <div className="max-w-6xl mx-auto p-8">
      <DashboardHeader />
      {error && (
        <div className="mb-5 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">
            <strong>Error:</strong> {error}
          </p>
          <p className="text-xs text-red-600 mt-1">
            Please check that the backend services are running on {apiUrl}
          </p>
        </div>
      )}
      <div className="space-y-5">
        <FactCheckReport />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <HeadlineSummary />
          <div className="space-y-5">
            <SentimentAnalysis />
            <ForensicAnalysis />
          </div>
        </div>
        <BiasCheckReport />
        <UpcomingFeatures />
      </div>
    </div>;
}