"use client";

import Link from "next/link";
import type { TrendingTicker } from "@/app/types/market";

interface TrendingTickersProps {
  tickers: TrendingTicker[];
}

export default function TrendingTickers({ tickers }: TrendingTickersProps) {
  const getChangeColor = (changePercent: number) => {
    if (changePercent > 0) return "text-green-400 bg-green-900/20";
    if (changePercent < 0) return "text-red-400 bg-red-900/20";
    return "text-gray-400 bg-[#2a2a2a]";
  };

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-white mb-4">Trending Tickers</h2>
      <div className="space-y-3">
        {tickers.map((ticker) => (
          <Link key={ticker.ticker} href={`/stocks/${ticker.ticker}`} className="block border border-[#2a2a2a] bg-[#111111] rounded-lg p-4 hover:shadow-lg hover:border-blue-700 transition-all group">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-bold text-lg text-white group-hover:text-blue-400 transition-colors">{ticker.ticker}</span>
                  <svg className="w-4 h-4 text-blue-500 -rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                  <span className="text-sm text-gray-400">{ticker.company_name}</span>
                </div>
                <p className="text-sm text-gray-400 mb-2">{ticker.reason}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Volume: {ticker.volume.toLocaleString()}</span>
                  <span>News: {ticker.news_count} articles</span>
                </div>
              </div>
              <div className="text-right ml-4">
                <p className="text-xl font-bold text-white mb-1">${ticker.price.toFixed(2)}</p>
                <span className={`inline-block px-2 py-1 rounded text-sm font-medium ${getChangeColor(ticker.change_percent)}`}>
                  {ticker.change_percent > 0 ? "+" : ""}
                  {ticker.change_percent.toFixed(2)}%
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
      {tickers.length === 0 && <p className="text-center text-gray-500 py-4">No trending tickers available</p>}
    </div>
  );
}
