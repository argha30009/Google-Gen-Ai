import React from 'react';
import { HomeIcon, ShieldCheckIcon, TrendingUpIcon, BookmarkIcon, BellIcon, CheckCircleIcon } from 'lucide-react';
export function Sidebar() {
  const navItems = [{
    icon: HomeIcon,
    label: 'Home',
    active: true
  }, {
    icon: ShieldCheckIcon,
    label: 'Verify',
    active: false
  }, {
    icon: TrendingUpIcon,
    label: 'Trending',
    active: false
  }, {
    icon: BookmarkIcon,
    label: 'Saved',
    active: false
  }, {
    icon: BellIcon,
    label: 'Alerts',
    active: false
  }];
  const recentChecks = [{
    label: 'US election mailers'
  }, {
    label: 'Viral health tip'
  }];
  return <aside className="fixed left-0 top-0 h-screen w-44 bg-[#FBF9F6] border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-amber-800 rounded flex items-center justify-center">
            <span className="text-white text-xs font-bold">C</span>
          </div>
          <span className="font-semibold text-base">Clipse</span>
        </div>
      </div>
      <nav className="flex-1 p-3">
        <ul className="space-y-0.5">
          {navItems.map(item => <li key={item.label}>
              <button className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-sm transition-colors ${item.active ? 'bg-[#E8DFC8] text-gray-900 font-medium' : 'text-gray-600 hover:bg-gray-100'}`}>
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            </li>)}
        </ul>
        <div className="mt-6">
          <h3 className="px-3 text-xs font-medium text-gray-500 mb-2">
            Recent checks
          </h3>
          <ul className="space-y-0.5">
            {recentChecks.map(item => <li key={item.label}>
                <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-sm text-gray-600 hover:bg-gray-100 transition-colors">
                  <CheckCircleIcon className="w-3.5 h-3.5" />
                  <span className="text-xs">{item.label}</span>
                </button>
              </li>)}
          </ul>
        </div>
      </nav>
      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 leading-relaxed">
          Trusted news verification, simplified.
        </p>
      </div>
    </aside>;
}