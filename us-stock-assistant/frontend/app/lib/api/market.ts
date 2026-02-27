import { apiClient } from "../api-client";
import type { MarketOverview, TrendingTicker, SectorPerformance, MarketIndex, SentimentEvaluation } from "@/app/types/market";

export const marketApi = {
  // Get market overview data
  getMarketOverview: async (): Promise<MarketOverview> => {
    const response = await apiClient.get("/api/market/overview");
    return response.data;
  },

  // Get trending tickers
  getTrendingTickers: async (limit: number = 10): Promise<TrendingTicker[]> => {
    const response = await apiClient.get("/api/market/trending", {
      params: { limit },
    });
    return response.data;
  },

  // Get sector performance
  getSectorPerformance: async (): Promise<SectorPerformance[]> => {
    const response = await apiClient.get("/api/market/sectors");
    return response.data;
  },

  // Get market indices
  getMarketIndices: async (): Promise<MarketIndex[]> => {
    const response = await apiClient.get("/api/market/indices");
    return response.data;
  },

  // Evaluate market sentiment accuracy using LLM
  evaluateMarketSentiment: async (): Promise<SentimentEvaluation> => {
    const response = await apiClient.post("/api/market/sentiment/evaluate");
    return response.data;
  },
};
