"use client";

import { useState } from "react";
import { NewsArticle } from "../types/news";

interface PaginatedNewsFeedProps {
  articles: NewsArticle[];
  itemsPerPage?: number;
  className?: string;
}

/**
 * Paginated news feed component
 * Limits initial data load and provides pagination controls
 */
export default function PaginatedNewsFeed({ articles, itemsPerPage = 10, className = "" }: PaginatedNewsFeedProps) {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(articles.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentArticles = articles.slice(startIndex, endIndex);

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
    // Scroll to top of feed
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "text-green-600 bg-green-50";
      case "negative":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  return (
    <div className={className}>
      {/* Articles */}
      <div className="space-y-4">
        {currentArticles.map((article) => (
          <div key={article.id} className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <a href={article.url} target="_blank" rel="noopener noreferrer" className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors">
                  {article.headline}
                </a>
                <p className="text-sm text-gray-600 mt-1">{article.summary}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <span>{article.source}</span>
                  <span>•</span>
                  <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
                </div>
              </div>
              {article.sentiment && <div className={`px-3 py-1 rounded-full text-xs font-medium ${getSentimentColor(article.sentiment.label)}`}>{article.sentiment.label}</div>}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {startIndex + 1}-{Math.min(endIndex, articles.length)} of {articles.length} articles
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => goToPage(currentPage - 1)} disabled={currentPage === 1} className="px-3 py-1 rounded border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
              Previous
            </button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }

                return (
                  <button key={pageNum} onClick={() => goToPage(pageNum)} className={`px-3 py-1 rounded text-sm font-medium ${currentPage === pageNum ? "bg-blue-600 text-white" : "text-gray-700 hover:bg-gray-100"}`}>
                    {pageNum}
                  </button>
                );
              })}
            </div>
            <button onClick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages} className="px-3 py-1 rounded border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
