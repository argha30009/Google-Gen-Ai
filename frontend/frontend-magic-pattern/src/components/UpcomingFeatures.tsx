import React from 'react';
import { LinkIcon, UsersIcon, GlobeIcon } from 'lucide-react';
export function UpcomingFeatures() {
  const features = [{
    icon: LinkIcon,
    title: 'Cross-Platform Claim Match',
    description: 'Placeholder: Automatically detect similar claims across X, Reddit, and major newswires.',
    color: 'bg-green-50 text-green-600'
  }, {
    icon: UsersIcon,
    title: 'Community Evidence',
    description: 'Placeholder: Submit citations and vote on reliability to improve report confidence.',
    color: 'bg-blue-50 text-blue-600'
  }, {
    icon: GlobeIcon,
    title: 'Multilingual Summaries',
    description: 'Placeholder: Auto-translate headline clusters and bias spectrums into 20+ languages.',
    color: 'bg-purple-50 text-purple-600'
  }];
  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-4">
        Upcoming Features
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {features.map(feature => <div key={feature.title} className="p-4 border border-gray-200 rounded-lg">
            <div className={`w-10 h-10 ${feature.color} rounded-lg flex items-center justify-center mb-3`}>
              <feature.icon className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-gray-900 mb-2">
              {feature.title}
            </h3>
            <p className="text-xs text-gray-600 leading-relaxed">
              {feature.description}
            </p>
          </div>)}
      </div>
    </div>;
}