import { apiClient } from "../api-client";
import type { StockPrice, HistoricalData, StockSearchResult, CompanyInfo, FinancialMetrics } from "@/app/types/stocks";

export const stocksApi = {
  // Get current stock price
  getCurrentPrice: async (ticker: string): Promise<StockPrice> => {
    const response = await apiClient.get(`/api/stocks/${ticker}/price`);
    return response.data;
  },

  // Get multiple stock prices (batch)
  getBatchPrices: async (tickers: string[]): Promise<Record<string, StockPrice>> => {
    const response = await apiClient.post("/api/stocks/prices/batch", { tickers });
    return response.data;
  },

  // Get historical price data
  getHistoricalData: async (ticker: string, startDate: string, endDate: string): Promise<HistoricalData[]> => {
    const response = await apiClient.get(`/api/stocks/${ticker}/historical`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  // Search for stocks
  searchStocks: async (query: string): Promise<StockSearchResult[]> => {
    const response = await apiClient.get("/api/stocks/search", {
      params: { q: query },
    });
    return response.data;
  },

  // Get company information
  getCompanyInfo: async (ticker: string): Promise<CompanyInfo> => {
    const response = await apiClient.get(`/api/stocks/${ticker}/company`);
    return response.data;
  },

  // Get financial metrics
  getFinancialMetrics: async (ticker: string): Promise<FinancialMetrics> => {
    const response = await apiClient.get(`/api/stocks/${ticker}/metrics`);
    return response.data;
  },

  // Get complete stock details (price, company, metrics)
  getStockDetails: async (
    ticker: string,
  ): Promise<{
    price: StockPrice;
    company: CompanyInfo;
    metrics: FinancialMetrics;
  }> => {
    const response = await apiClient.get(`/api/stocks/${ticker}`);
    return response.data;
  },
};
