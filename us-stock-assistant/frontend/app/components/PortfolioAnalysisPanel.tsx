"use client";

import { useState } from "react";
import { analysisApi } from "@/app/lib/api/analysis";
import type { PortfolioAnalysis } from "@/app/types/analysis";
import { handleApiError } from "@/app/lib/api-client";

export default function PortfolioAnalysisPanel() {
  const [analysis, setAnalysis] = useState<PortfolioAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await analysisApi.analyzePortfolio();
      setAnalysis(result);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case "good":
        return "text-green-400 bg-green-900/20 border-green-700";
      case "fair":
        return "text-yellow-400 bg-yellow-900/20 border-yellow-700";
      case "poor":
        return "text-red-400 bg-red-900/20 border-red-700";
      default:
        return "text-gray-400 bg-[#1a1a1a] border-[#2a2a2a]";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "low":
        return "text-green-400 bg-green-900/20";
      case "medium":
        return "text-yellow-400 bg-yellow-900/20";
      case "high":
        return "text-red-400 bg-red-900/20";
      default:
        return "text-gray-400 bg-[#2a2a2a]";
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "buy":
        return "text-green-400 bg-green-900/20";
      case "sell":
        return "text-red-400 bg-red-900/20";
      case "hold":
        return "text-gray-400 bg-[#2a2a2a]";
      default:
        return "text-gray-400 bg-[#2a2a2a]";
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case "good":
        return (
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case "fair":
        return (
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case "poor":
        return (
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Portfolio Analysis</h2>
        <button onClick={handleAnalyze} disabled={isLoading} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium">
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Analyzing...
            </span>
          ) : (
            "Analyze Portfolio"
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
              <p className="text-xs text-red-500 mt-2">This could be due to insufficient portfolio data, API limitations, or temporary service issues. Please try again later.</p>
              <button onClick={handleAnalyze} className="mt-3 text-sm text-red-400 hover:text-red-300 font-medium underline">
                Retry Analysis
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-6">
          <div className="animate-pulse">
            <div className="h-32 bg-[#2a2a2a] rounded-lg mb-4"></div>
            <div className="h-24 bg-[#2a2a2a] rounded-lg mb-4"></div>
            <div className="h-48 bg-[#2a2a2a] rounded-lg"></div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !isLoading && (
        <div className="space-y-6">
          {/* Overall Health Score */}
          <div className={`border-2 rounded-lg p-6 ${getHealthColor(analysis.overall_health)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2 text-white">Overall Portfolio Health</h3>
                <p className="text-3xl font-bold capitalize">{analysis.overall_health}</p>
              </div>
              <div className={getHealthColor(analysis.overall_health).split(" ")[0]}>{getHealthIcon(analysis.overall_health)}</div>
            </div>
          </div>

          {/* Diversification Analysis */}
          <div className="bg-[#111111] rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Diversification Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a]">
                <span className="text-sm text-gray-400">Diversification Score</span>
                <div className="flex items-end gap-2 mt-2">
                  <p className="text-3xl font-bold text-white">{analysis.diversification_score.toFixed(1)}</p>
                  <span className="text-sm text-gray-500 mb-1">/ 100</span>
                </div>
                <div className="mt-3 bg-[#2a2a2a] rounded-full h-2 overflow-hidden">
                  <div className={`h-full rounded-full ${analysis.diversification_score >= 70 ? "bg-green-500" : analysis.diversification_score >= 40 ? "bg-yellow-500" : "bg-red-500"}`} style={{ width: `${analysis.diversification_score}%` }}></div>
                </div>
              </div>
              <div className="bg-[#1a1a1a] rounded-lg p-4 border border-[#2a2a2a]">
                <span className="text-sm text-gray-400">Risk Level</span>
                <div className="mt-2">
                  <span className={`inline-block px-4 py-2 rounded-full text-lg font-semibold capitalize ${getRiskColor(analysis.risk_level)}`}>{analysis.risk_level}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Rebalancing Suggestions */}
          {analysis.rebalancing_suggestions.length > 0 && (
            <div className="bg-[#1a1a1a] rounded-lg border border-[#2a2a2a] overflow-hidden">
              <div className="bg-[#111111] px-6 py-4 border-b border-[#2a2a2a]">
                <h3 className="text-lg font-semibold text-white">Rebalancing Suggestions</h3>
              </div>
              <div className="divide-y divide-[#2a2a2a]">
                {analysis.rebalancing_suggestions.map((suggestion, index) => (
                  <div key={index} className="p-4 hover:bg-[#222222] transition-colors">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-lg font-semibold text-white">{suggestion.ticker}</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getActionColor(suggestion.action)}`}>{suggestion.action}</span>
                    </div>
                    <p className="text-sm text-gray-300 mb-2">{suggestion.reason}</p>
                    <p className="text-sm text-gray-400">
                      Suggested Amount: <span className="font-medium">${suggestion.suggested_amount.toFixed(2)}</span>
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Underperforming Stocks */}
          {analysis.underperforming_stocks.length > 0 && (
            <div className="bg-red-900/20 rounded-lg border border-red-800 p-6">
              <h3 className="text-lg font-semibold text-red-400 mb-3 flex items-center">
                <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                </svg>
                Underperforming Stocks
              </h3>
              <div className="flex flex-wrap gap-2">
                {analysis.underperforming_stocks.map((ticker, index) => (
                  <span key={index} className="px-3 py-1 bg-[#1a1a1a] border border-red-800 text-red-400 rounded-lg text-sm font-medium">
                    {ticker}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Opportunities */}
          {analysis.opportunities.length > 0 && (
            <div className="bg-green-900/20 rounded-lg border border-green-800 p-6">
              <h3 className="text-lg font-semibold text-green-400 mb-3 flex items-center">
                <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                Opportunities
              </h3>
              <ul className="space-y-2">
                {analysis.opportunities.map((opportunity, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="h-5 w-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-gray-300">{opportunity}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!analysis && !isLoading && !error && (
        <div className="text-center py-12">
          <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-300 text-lg mb-2">Get AI-Powered Portfolio Insights</p>
          <p className="text-gray-500 text-sm">Click "Analyze Portfolio" to receive personalized recommendations, diversification analysis, and rebalancing suggestions.</p>
        </div>
      )}
    </div>
  );
}
