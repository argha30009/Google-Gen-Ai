import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface NewsData {
  query: string;
  search_results: {
    headlines: Array<{
      title: string;
      query: string;
    }>;
    message?: string;
  };
  sentiment_analysis: {
    sentiment_summary: {
      overall: string;
      positive_count: number;
      negative_count: number;
      neutral_count: number;
      total_analyzed: number;
    };
    per_item: Array<{
      headline: string;
      sentiment: string;
      polarity: number;
      subjectivity: number;
    }>;
    message?: string;
  };
  trends_analysis: {
    message?: string;
    trend_data?: any;
    plot_url?: string;
  };
  summary: {
    overview: string;
    sentiment_overview: string;
    sentiment_summary: string;
    fact_check: string;
    bias_check: string;
    forensic_analysis: string;
  };
  status?: string;
}

interface NewsContextType {
  newsData: NewsData | null;
  loading: boolean;
  error: string | null;
  fetchNews: (query: string) => Promise<void>;
}

const NewsContext = createContext<NewsContextType | undefined>(undefined);

export function NewsProvider({ children }: { children: ReactNode }) {
  const [newsData, setNewsData] = useState<NewsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNews = async (query: string) => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    console.log('Fetching news for query:', query);
    setLoading(true);
    setError(null);

    try {
      console.log('Sending request to backend...');
      // Use Cloud Run URL if available, fallback to localhost
      const apiUrl = import.meta.env.VITE_API_URL || 'https://manager-agent-466223788759.asia-south1.run.app';
      const response = await fetch(`${apiUrl}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Received data:', data);
      console.log('📰 Headlines count:', data.search_results?.headlines?.length);
      console.log('💭 Sentiment data:', data.sentiment_analysis);
      console.log('📋 Summary data:', data.summary);
      
      setNewsData(data);
      console.log('🎯 News data set successfully in context');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      console.error('❌ Error fetching news:', errorMessage);
      setError(errorMessage);
    } finally {
      setLoading(false);
      console.log('🏁 Fetch complete, loading state set to false');
    }
  };

  return (
    <NewsContext.Provider value={{ newsData, loading, error, fetchNews }}>
      {children}
    </NewsContext.Provider>
  );
}

export function useNews() {
  const context = useContext(NewsContext);
  if (context === undefined) {
    throw new Error('useNews must be used within a NewsProvider');
  }
  return context;
}
