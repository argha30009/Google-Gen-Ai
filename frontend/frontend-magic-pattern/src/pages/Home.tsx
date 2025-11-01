import React from 'react';
import { Header } from '../components/Header';
import { SearchBar } from '../components/SearchBar';
import { RecentHeadlines } from '../components/RecentHeadlines';
import { PopularThisWeek } from '../components/PopularThisWeek';
import { QuickSuggestions } from '../components/QuickSuggestions';
export function Home() {
  return <div className="max-w-5xl mx-auto p-8">
      <Header />
      <SearchBar />
      <div className="space-y-5">
        <RecentHeadlines />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <PopularThisWeek />
          <QuickSuggestions />
        </div>
      </div>
    </div>;
}