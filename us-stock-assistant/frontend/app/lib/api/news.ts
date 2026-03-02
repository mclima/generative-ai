import { apiClient } from "../api-client";
import type { NewsArticle, StockSentiment } from "@/app/types/news";

export const newsApi = {
  // Get news for a specific stock
  getStockNews: async (ticker: string, limit: number = 10): Promise<NewsArticle[]> => {
    const response = await apiClient.get(`/api/news/stock/${ticker}`, {
      params: { limit },
    });
    return response.data;
  },

  // Get general market news
  getMarketNews: async (limit: number = 20): Promise<NewsArticle[]> => {
    const response = await apiClient.get("/api/news/market", {
      params: { limit },
    });
    return response.data;
  },

  // Get overall sentiment for a stock
  getStockSentiment: async (ticker: string): Promise<StockSentiment> => {
    const response = await apiClient.get(`/api/news/stock/${ticker}/sentiment`);
    return response.data;
  },

  // Evaluate stock sentiment with AI
  evaluateStockSentiment: async (ticker: string): Promise<{
    calculated_sentiment: { label: string; score: number; confidence: number };
    llm_evaluation: string;
    accuracy_assessment: string;
    confidence_level: string;
    recommendations: string[];
  }> => {
    const response = await apiClient.post(`/api/news/stock/${ticker}/sentiment/evaluate`);
    return response.data;
  },
};
