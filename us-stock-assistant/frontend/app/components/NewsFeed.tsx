"use client";

import { useState, useEffect } from "react";
import type { NewsArticle } from "@/app/types/news";
import { newsApi } from "@/app/lib/api/news";
import { usePreferences } from "@/app/contexts/PreferencesContext";

interface NewsFeedProps {
  filterTicker?: string;
  limit?: number;
}

export default function NewsFeed({ filterTicker, limit = 20 }: NewsFeedProps) {
  const { preferences } = usePreferences();
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const articlesPerPage = 10;

  useEffect(() => {
    loadNews();
  }, [filterTicker]);

  const loadNews = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = filterTicker ? await newsApi.getStockNews(filterTicker, limit) : await newsApi.getMarketNews(limit);

      // Filter by preferred news sources if configured
      const filteredData = preferences?.preferred_news_sources && preferences.preferred_news_sources.length > 0 ? data.filter((article) => preferences.preferred_news_sources.includes(article.source)) : data;

      setArticles(filteredData);
      setHasMore(filteredData.length >= articlesPerPage);
      setPage(1);
    } catch (err) {
      setError("Failed to load news. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const loadMore = () => {
    const nextPage = page + 1;
    const endIndex = nextPage * articlesPerPage;

    if (endIndex >= articles.length) {
      setHasMore(false);
    }

    setPage(nextPage);
  };

  const getSentimentColor = (label?: string) => {
    switch (label) {
      case "positive":
        return "text-green-600 bg-green-50";
      case "negative":
        return "text-red-600 bg-red-50";
      case "neutral":
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getSentimentIcon = (label?: string) => {
    switch (label) {
      case "positive":
        return "↑";
      case "negative":
        return "↓";
      case "neutral":
      default:
        return "→";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const displayedArticles = articles.slice(0, page * articlesPerPage);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error}</p>
        <button onClick={loadNews} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Retry
        </button>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No news articles available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {displayedArticles.map((article) => (
        <div key={article.id} className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors">
                {article.headline}
              </a>

              <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
                <span className="font-medium">{article.source}</span>
                <span>•</span>
                <span>{formatTimestamp(article.published_at)}</span>
              </div>

              {article.summary && <p className="mt-3 text-gray-700 text-sm line-clamp-2">{article.summary}</p>}
            </div>

            {article.sentiment && (
              <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap ${getSentimentColor(article.sentiment.label)}`}>
                <span>{getSentimentIcon(article.sentiment.label)}</span>
                <span className="capitalize">{article.sentiment.label}</span>
              </div>
            )}
          </div>
        </div>
      ))}

      {hasMore && displayedArticles.length < articles.length && (
        <div className="text-center pt-4">
          <button onClick={loadMore} className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            Load More
          </button>
        </div>
      )}
    </div>
  );
}
