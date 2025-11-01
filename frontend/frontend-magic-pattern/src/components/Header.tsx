import React from 'react';
import { PlusIcon, HelpCircleIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
export function Header() {
  const navigate = useNavigate();
  return <div className="flex items-center justify-between mb-6">
      <h1 className="text-2xl font-semibold text-gray-900">
        Verify news with confidence
      </h1>
      <div className="flex items-center gap-2">
        <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <HelpCircleIcon className="w-4 h-4" />
          How it works
        </button>
        <button onClick={() => navigate('/dashboard')} className="flex items-center gap-2 px-4 py-2 text-sm bg-amber-800 hover:bg-amber-900 text-white rounded-lg transition-colors">
          <PlusIcon className="w-4 h-4" />
          New check
        </button>
      </div>
    </div>;
}