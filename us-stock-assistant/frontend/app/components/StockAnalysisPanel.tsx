"use client";

import { useState } from "react";
import { analysisApi } from "@/app/lib/api/analysis";
import type { StockAnalysis } from "@/app/types/analysis";
import { handleApiError } from "@/app/lib/api-client";

interface StockAnalysisPanelProps {
  ticker: string;
}

export default function StockAnalysisPanel({ ticker }: StockAnalysisPanelProps) {
  const [analysis, setAnalysis] = useState<StockAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["summary"]));

  const handleAnalyze = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await analysisApi.analyzeStock(ticker);
      setAnalysis(result);
      // Expand all sections by default when analysis loads
      setExpandedSections(new Set(["summary", "price", "sentiment", "recommendations", "risks"]));
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "bullish":
        return "text-green-400 bg-green-900/20";
      case "bearish":
        return "text-red-400 bg-red-900/20";
      default:
        return "text-gray-400 bg-[#2a2a2a]";
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "text-green-400 bg-green-900/20";
      case "negative":
        return "text-red-400 bg-red-900/20";
      default:
        return "text-gray-400 bg-[#2a2a2a]";
    }
  };

  const getVolatilityColor = (volatility: string) => {
    switch (volatility) {
      case "high":
        return "text-red-400 bg-red-900/20";
      case "medium":
        return "text-yellow-400 bg-yellow-900/20";
      default:
        return "text-green-400 bg-green-900/20";
    }
  };

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">AI Analysis</h2>
        <button onClick={handleAnalyze} disabled={isLoading} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-[#2a2a2a] disabled:text-gray-500 disabled:cursor-not-allowed transition-colors font-medium">
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Analyzing...
            </span>
          ) : (
            "Analyze"
          )}
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-4 mb-4">
          <div className="flex items-start">
            <svg className="h-5 w-5 text-red-600 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-400 mb-1">Analysis Failed</h3>
              <p className="text-sm text-red-400">{error}</p>
              <p className="text-xs text-red-500 mt-2">This could be due to insufficient data, API limitations, or temporary service issues. Please try again later.</p>
              <button onClick={handleAnalyze} className="mt-3 text-sm text-red-400 hover:text-red-300 font-medium underline">
                Retry Analysis
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-4">
          <div className="animate-pulse">
            <div className="h-4 bg-[#2a2a2a] rounded w-3/4 mb-3"></div>
            <div className="h-4 bg-[#2a2a2a] rounded w-full mb-3"></div>
            <div className="h-4 bg-[#2a2a2a] rounded w-5/6"></div>
          </div>
          <div className="animate-pulse">
            <div className="h-32 bg-[#2a2a2a] rounded"></div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !isLoading && (
        <div className="space-y-4">
          {/* Summary Section */}
          <div className="border border-[#2a2a2a] rounded-lg overflow-hidden">
            <button onClick={() => toggleSection("summary")} className="w-full flex items-center justify-between p-4 bg-[#111111] hover:bg-[#222222] transition-colors">
              <h3 className="text-lg font-semibold text-white">Summary</h3>
              <svg className={`h-5 w-5 text-gray-400 transition-transform ${expandedSections.has("summary") ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedSections.has("summary") && (
              <div className="p-4 bg-[#1a1a1a]">
                <p className="text-gray-300 leading-relaxed">{analysis.summary}</p>
                <p className="text-xs text-gray-500 mt-3">Generated: {new Date(analysis.generated_at).toLocaleString()}</p>
              </div>
            )}
          </div>

          {/* Price Analysis Section */}
          <div className="border border-[#2a2a2a] rounded-lg overflow-hidden">
            <button onClick={() => toggleSection("price")} className="w-full flex items-center justify-between p-4 bg-[#111111] hover:bg-[#222222] transition-colors">
              <h3 className="text-lg font-semibold text-white">Price Trends</h3>
              <svg className={`h-5 w-5 text-gray-400 transition-transform ${expandedSections.has("price") ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedSections.has("price") && (
              <div className="p-4 bg-[#1a1a1a] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Trend:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getTrendColor(analysis.price_analysis.trend)}`}>{analysis.price_analysis.trend}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Volatility:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getVolatilityColor(analysis.price_analysis.volatility)}`}>{analysis.price_analysis.volatility}</span>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div>
                    <span className="text-sm text-gray-400">Support Level:</span>
                    <p className="text-lg font-semibold text-white">{analysis.price_analysis.support != null ? `$${analysis.price_analysis.support.toFixed(2)}` : "N/A"}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-400">Resistance Level:</span>
                    <p className="text-lg font-semibold text-white">{analysis.price_analysis.resistance != null ? `$${analysis.price_analysis.resistance.toFixed(2)}` : "N/A"}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sentiment Analysis Section */}
          <div className="border border-[#2a2a2a] rounded-lg overflow-hidden">
            <button onClick={() => toggleSection("sentiment")} className="w-full flex items-center justify-between p-4 bg-[#111111] hover:bg-[#222222] transition-colors">
              <h3 className="text-lg font-semibold text-white">Market Sentiment</h3>
              <svg className={`h-5 w-5 text-gray-400 transition-transform ${expandedSections.has("sentiment") ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedSections.has("sentiment") && (
              <div className="p-4 bg-[#1a1a1a] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Overall Sentiment:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getSentimentColor(analysis.sentiment_analysis.overall)}`}>{analysis.sentiment_analysis.overall}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Sentiment Score:</span>
                  <span className="text-lg font-semibold text-white">{analysis.sentiment_analysis.score != null ? analysis.sentiment_analysis.score.toFixed(2) : "N/A"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Based on:</span>
                  <span className="text-sm text-gray-300">{analysis.sentiment_analysis.news_count} news articles</span>
                </div>
              </div>
            )}
          </div>

          {/* Recommendations Section */}
          <div className="border border-[#2a2a2a] rounded-lg overflow-hidden">
            <button onClick={() => toggleSection("recommendations")} className="w-full flex items-center justify-between p-4 bg-[#111111] hover:bg-[#222222] transition-colors">
              <h3 className="text-lg font-semibold text-white">Recommendations</h3>
              <svg className={`h-5 w-5 text-gray-400 transition-transform ${expandedSections.has("recommendations") ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedSections.has("recommendations") && (
              <div className="p-4 bg-[#1a1a1a]">
                <ul className="space-y-2">
                  {analysis.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start">
                      <svg className="h-5 w-5 text-green-400 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-gray-300">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Risks Section */}
          <div className="border border-[#2a2a2a] rounded-lg overflow-hidden">
            <button onClick={() => toggleSection("risks")} className="w-full flex items-center justify-between p-4 bg-[#111111] hover:bg-[#222222] transition-colors">
              <h3 className="text-lg font-semibold text-white">Risks</h3>
              <svg className={`h-5 w-5 text-gray-400 transition-transform ${expandedSections.has("risks") ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedSections.has("risks") && (
              <div className="p-4 bg-[#1a1a1a]">
                <ul className="space-y-2">
                  {analysis.risks.map((risk, index) => (
                    <li key={index} className="flex items-start">
                      <svg className="h-5 w-5 text-red-400 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <span className="text-gray-300">{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!analysis && !isLoading && !error && (
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <p className="text-gray-400">Click "Analyze" to get AI-powered insights for {ticker}</p>
        </div>
      )}
    </div>
  );
}
