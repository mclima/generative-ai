"use client";

import { useState, useEffect } from "react";
import type { NewsArticle, StockSentiment } from "@/app/types/news";
import { newsApi } from "@/app/lib/api/news";

interface StockNewsSectionProps {
  ticker: string;
  limit?: number;
}

export default function StockNewsSection({ ticker, limit = 5 }: StockNewsSectionProps) {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [sentiment, setSentiment] = useState<StockSentiment | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ticker) {
      loadStockNews();
    }
  }, [ticker]);

  const loadStockNews = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [newsData, sentimentData] = await Promise.allSettled([newsApi.getStockNews(ticker, limit), newsApi.getStockSentiment(ticker)]);

      if (newsData.status === "fulfilled") {
        setArticles(newsData.value);
      }

      if (sentimentData.status === "fulfilled") {
        setSentiment(sentimentData.value);
      }

      if (newsData.status === "rejected" && sentimentData.status === "rejected") {
        setError("Failed to load news data. Please try again.");
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const getSentimentColor = (label?: string) => {
    switch (label) {
      case "positive":
        return "text-green-400 bg-green-900/20 border-green-800";
      case "negative":
        return "text-red-400 bg-red-900/20 border-red-800";
      case "neutral":
      default:
        return "text-gray-400 bg-[#2a2a2a] border-[#3a3a3a]";
    }
  };

  const getSentimentIcon = (label?: string) => {
    switch (label) {
      case "positive":
        return (
          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
          </svg>
        );
      case "negative":
        return (
          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
          </svg>
        );
      case "neutral":
      default:
        return (
          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v4a1 1 0 002 0V7z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (isLoading) {
    return (
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">News &amp; Sentiment</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      </div>
    );
  }

  if (error && !articles.length && !sentiment) {
    return (
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">News &amp; Sentiment</h2>
        <div className="text-center py-8">
          <p className="text-red-400 mb-4">{error}</p>
          <button onClick={loadStockNews} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
      <h2 className="text-xl font-bold text-white mb-4">News &amp; Sentiment</h2>

      {/* Overall Sentiment Summary */}
      {sentiment && (
        <div className={`mb-6 p-4 rounded-lg border-2 ${getSentimentColor(sentiment.overall_sentiment.label)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getSentimentIcon(sentiment.overall_sentiment.label)}
              <div>
                <p className="font-semibold text-lg capitalize">{sentiment.overall_sentiment.label} Sentiment</p>
                <p className="text-sm opacity-75">Based on {sentiment.article_count} recent articles</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold">{sentiment.overall_sentiment.score >= 0 ? "+" : ""}{sentiment.overall_sentiment.score.toFixed(2)}</p>
              <p className="text-xs opacity-75">Score (-1 to +1)</p>
            </div>
          </div>
        </div>
      )}

      {/* Recent News Articles */}
      {articles.length > 0 ? (
        <div className="space-y-4">
          <h3 className="font-semibold text-white">Recent News</h3>
          {articles.map((article) => (
            <div key={article.id} className="border-l-4 border-[#2a2a2a] pl-4 py-2 hover:border-blue-500 transition-colors">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <a href={article.url} target="_blank" rel="noopener noreferrer" className="font-medium text-white hover:text-blue-400 transition-colors">
                    {article.headline}
                  </a>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    <span>{article.source}</span>
                    <span>•</span>
                    <span>{formatTimestamp(article.published_at)}</span>
                  </div>
                  {article.summary && <p className="mt-2 text-sm text-gray-400 line-clamp-2">{article.summary}</p>}
                </div>
                {article.sentiment && <span className={`px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${getSentimentColor(article.sentiment.label)}`}>{article.sentiment.label}</span>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-center py-4">No recent news available for {ticker}</p>
      )}
    </div>
  );
}
