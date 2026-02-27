import { apiClient } from "../api-client";
import type { StockAnalysis, PortfolioAnalysis } from "@/app/types/analysis";

export const analysisApi = {
  // Get AI analysis for a stock
  analyzeStock: async (ticker: string): Promise<StockAnalysis> => {
    const response = await apiClient.post(`/api/analysis/stock/${ticker}`);
    return response.data;
  },

  // Get portfolio analysis
  analyzePortfolio: async (): Promise<PortfolioAnalysis> => {
    const response = await apiClient.post("/api/analysis/portfolio");
    return response.data;
  },
};
