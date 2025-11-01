import React from 'react';
import { DashboardHeader } from '../components/DashboardHeader';
import { FactCheckReport } from '../components/FactCheckReport';
import { HeadlineSummary } from '../components/HeadlineSummary';
import { SentimentAnalysis } from '../components/SentimentAnalysis';
import { ForensicAnalysis } from '../components/ForensicAnalysis';
import { BiasCheckReport } from '../components/BiasCheckReport';
import { UpcomingFeatures } from '../components/UpcomingFeatures';
export function Dashboard() {
  return <div className="max-w-6xl mx-auto p-8">
      <DashboardHeader />
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