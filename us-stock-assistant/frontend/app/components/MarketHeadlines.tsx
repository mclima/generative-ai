"use client";

import type { NewsArticle } from "@/app/types/news";

interface MarketHeadlinesProps {
  headlines: NewsArticle[];
}

export default function MarketHeadlines({ headlines }: MarketHeadlinesProps) {
  const getSentimentColor = (label?: string) => {
    switch (label) {
      case "positive":
        return "text-green-400 bg-green-900/20 border-green-700";
      case "negative":
        return "text-red-400 bg-red-900/20 border-red-700";
      case "neutral":
      default:
        return "text-gray-400 bg-[#2a2a2a] border-[#3a3a3a]";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / 60000);
      return `${diffMinutes}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-white mb-4">Top Market Headlines</h2>
      <div className="space-y-4">
        {headlines.map((article) => (
          <div key={article.id} className="border-l-4 border-[#2a2a2a] pl-4 py-2 hover:border-blue-500 transition-colors">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <a href={article.url} target="_blank" rel="noopener noreferrer" className="font-medium text-white hover:text-blue-400 transition-colors">
                  {article.headline}
                </a>
                <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                  <span className="font-medium">{article.source}</span>
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
      {headlines.length === 0 && <p className="text-center text-gray-500 py-4">No headlines available</p>}
    </div>
  );
}
