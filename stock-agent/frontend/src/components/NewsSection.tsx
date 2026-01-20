"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Newspaper, ExternalLink, Loader2 } from "lucide-react";
import { format } from "date-fns";

interface NewsSectionProps {
  symbol: string;
  data?: NewsArticle[];
  isLoading?: boolean;
}

interface NewsArticle {
  title: string;
  description: string;
  url: string;
  published_at: string;
  source: string;
  sentiment?: "positive" | "negative" | "neutral";
}

export default function NewsSection({ symbol, data: initialData, isLoading: externalLoading }: NewsSectionProps) {
  const [news, setNews] = useState<NewsArticle[]>(initialData || []);
  const [loading, setLoading] = useState(!initialData);

  useEffect(() => {
    if (initialData) {
      setNews(initialData);
      setLoading(false);
      return;
    }

    const fetchNews = async () => {
      setLoading(true);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await axios.get(`${apiUrl}/api/stock/${symbol}/news`);
        setNews(response.data);
      } catch (err) {
        console.error("Failed to fetch news:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [symbol, initialData]);

  const isLoading = externalLoading !== undefined ? externalLoading : loading;

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case "positive":
        return "bg-success/20 text-success border-success/50";
      case "negative":
        return "bg-danger/20 text-danger border-danger/50";
      default:
        return "bg-gray-700/20 text-gray-400 border-gray-600/50";
    }
  };

  return (
    <div className="card">
      <div className="flex items-center mb-6">
        <Newspaper className="w-6 h-6 text-blue-500 mr-2" />
        <h3 className="text-xl font-semibold">Latest News</h3>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="space-y-4">
          {news.map((article, index) => (
            <div
              key={index}
              className="bg-gray-800/50 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-lg flex-1 pr-4">{article.title}</h4>
                {article.sentiment && (
                  <span className={`px-2 py-1 rounded text-xs border ${getSentimentColor(article.sentiment)}`}>
                    {article.sentiment}
                  </span>
                )}
              </div>
              
              <p className="text-gray-400 text-sm mb-3">{article.description}</p>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-3">
                  <span>{article.source}</span>
                  <span>•</span>
                  <span>{format(new Date(article.published_at), "MMM d, yyyy")}</span>
                </div>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-primary hover:text-primary-dark transition-colors"
                >
                  Read more
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
