"use client";

import { useState, useEffect } from "react";
import type { MarketOverview as MarketOverviewType } from "@/app/types/market";
import { marketApi } from "@/app/lib/api/market";
import MarketIndices from "./MarketIndices";
import MarketHeadlines from "./MarketHeadlines";
import MarketSentiment from "./MarketSentiment";
import TrendingTickers from "./TrendingTickers";
import SectorHeatmap from "./SectorHeatmap";

export default function MarketOverview() {
  const [marketData, setMarketData] = useState<MarketOverviewType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMarketOverview();

    // Refresh market data every 15 minutes
    const interval = setInterval(loadMarketOverview, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadMarketOverview = async () => {
    try {
      setError(null);
      const data = await marketApi.getMarketOverview();
      setMarketData(data);
    } catch (err) {
      setError("Failed to load market overview. Please try again.");
      console.error("Error loading market overview:", err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (error || !marketData) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error || "No market data available"}</p>
        <button onClick={loadMarketOverview} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Market Indices */}
      <MarketIndices indices={marketData.indices} />

      {/* Market Sentiment */}
      <MarketSentiment sentiment={marketData.sentiment} indices={marketData.indices} />

      {/* Trending Tickers */}
      <TrendingTickers tickers={marketData.trending_tickers} />

      {/* Market Headlines */}
      <MarketHeadlines headlines={marketData.headlines} />

      {/* Sector Heatmap (optional feature) */}
      {marketData.sector_heatmap && marketData.sector_heatmap.length > 0 && <SectorHeatmap sectors={marketData.sector_heatmap} />}

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500">Last updated: {new Date(marketData.last_updated).toLocaleString()}</div>
    </div>
  );
}
