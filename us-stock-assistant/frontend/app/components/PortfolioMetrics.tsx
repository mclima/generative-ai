"use client";

import type { PortfolioMetrics as PortfolioMetricsType } from "@/app/types/portfolio";

interface PortfolioMetricsProps {
  metrics: PortfolioMetricsType;
  totalValue: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
}

export default function PortfolioMetrics({ metrics, totalValue, totalGainLoss, totalGainLossPercent }: PortfolioMetricsProps) {
  const { daily_gain_loss, diversity_score, performance_by_period } = metrics;

  const periods: Array<{ key: keyof typeof performance_by_period; label: string }> = [
    { key: "1D", label: "1 Day" },
    { key: "1W", label: "1 Week" },
    { key: "1M", label: "1 Month" },
    { key: "3M", label: "3 Months" },
    { key: "1Y", label: "1 Year" },
    { key: "ALL", label: "All Time" },
  ];

  const getDiversityColor = (score: number) => {
    if (score >= 8) return "text-green-600";
    if (score >= 5) return "text-yellow-600";
    return "text-red-600";
  };

  const getDiversityBgColor = (score: number) => {
    if (score >= 8) return "bg-green-600";
    if (score >= 5) return "bg-yellow-600";
    return "bg-red-600";
  };

  const getDiversityLabel = (score: number) => {
    if (score >= 8) return "Excellent";
    if (score >= 5) return "Good";
    return "Needs Improvement";
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Value */}
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-400">Total Value</p>
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-3xl font-bold text-white">${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>

        {/* Total Gain/Loss */}
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-400">Total Gain/Loss</p>
            <svg className={`w-5 h-5 ${totalGainLoss >= 0 ? "text-green-600" : "text-red-600"}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={totalGainLoss >= 0 ? "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" : "M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"} />
            </svg>
          </div>
          <p className={`text-3xl font-bold ${totalGainLoss >= 0 ? "text-green-600" : "text-red-600"}`}>
            {totalGainLoss >= 0 ? "+" : ""}${totalGainLoss.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className={`text-sm mt-1 ${totalGainLoss >= 0 ? "text-green-600" : "text-red-600"}`}>
            {totalGainLoss >= 0 ? "+" : ""}
            {totalGainLossPercent.toFixed(2)}%
          </p>
        </div>

        {/* Daily Change */}
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-400">Daily Change</p>
            <svg className={`w-5 h-5 ${daily_gain_loss >= 0 ? "text-green-600" : "text-red-600"}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className={`text-3xl font-bold ${daily_gain_loss >= 0 ? "text-green-600" : "text-red-600"}`}>
            {daily_gain_loss >= 0 ? "+" : ""}${daily_gain_loss.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="text-sm text-gray-500 mt-1">Today</p>
        </div>

        {/* Diversity Score */}
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-400">Diversity Score</p>
            <svg className={`w-5 h-5 ${getDiversityColor(diversity_score)}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div className="flex items-baseline gap-2">
            <p className={`text-3xl font-bold ${getDiversityColor(diversity_score)}`}>{diversity_score.toFixed(1)}</p>
            <p className="text-gray-500">/10</p>
          </div>
          <div className="mt-3">
            <div className="w-full bg-[#2a2a2a] rounded-full h-2">
              <div className={`h-2 rounded-full transition-all ${getDiversityBgColor(diversity_score)}`} style={{ width: `${(diversity_score / 10) * 100}%` }}></div>
            </div>
            <p className={`text-xs mt-1 ${getDiversityColor(diversity_score)}`}>{getDiversityLabel(diversity_score)}</p>
          </div>
        </div>
      </div>

      {/* Performance Over Time */}
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-white mb-6">Performance Over Time</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {periods.map(({ key, label }) => {
            const value = Number(performance_by_period[key]);
            const isPositive = value >= 0;

            return (
              <div key={key} className="text-center p-4 bg-[#111111] rounded-lg">
                <p className="text-sm text-gray-400 mb-2">{label}</p>
                <p className={`text-2xl font-bold ${isPositive ? "text-green-600" : "text-red-600"}`}>
                  {isPositive ? "+" : ""}
                  {value.toFixed(2)}%
                </p>
                <div className="mt-2">
                  {isPositive ? (
                    <svg className="w-5 h-5 mx-auto text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 mx-auto text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                    </svg>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
