import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CACHE_CONFIG } from "../providers/QueryProvider";
import { stocksApi } from "../lib/api/stocks";
import { StockPrice, HistoricalData, CompanyInfo, FinancialMetrics } from "../types/stocks";

// Query keys for cache management
export const stockKeys = {
  all: ["stocks"] as const,
  price: (ticker: string) => [...stockKeys.all, "price", ticker] as const,
  prices: (tickers: string[]) => [...stockKeys.all, "prices", tickers.sort().join(",")] as const,
  historical: (ticker: string, startDate: string, endDate: string) => [...stockKeys.all, "historical", ticker, startDate, endDate] as const,
  company: (ticker: string) => [...stockKeys.all, "company", ticker] as const,
  metrics: (ticker: string) => [...stockKeys.all, "metrics", ticker] as const,
  search: (query: string) => [...stockKeys.all, "search", query] as const,
};

// Hook for fetching current stock price
export function useStockPrice(ticker: string, enabled = true) {
  return useQuery({
    queryKey: stockKeys.price(ticker),
    queryFn: () => stocksApi.getCurrentPrice(ticker),
    staleTime: CACHE_CONFIG.stockPrice,
    enabled: enabled && !!ticker,
  });
}

// Hook for fetching multiple stock prices
export function useStockPrices(tickers: string[], enabled = true) {
  return useQuery({
    queryKey: stockKeys.prices(tickers),
    queryFn: () => stocksApi.getBatchPrices(tickers),
    staleTime: CACHE_CONFIG.stockPrice,
    enabled: enabled && tickers.length > 0,
  });
}

// Hook for fetching historical data
export function useHistoricalData(ticker: string, startDate: Date, endDate: Date, enabled = true) {
  const startStr = startDate.toISOString().split("T")[0];
  const endStr = endDate.toISOString().split("T")[0];

  return useQuery({
    queryKey: stockKeys.historical(ticker, startStr, endStr),
    queryFn: () => stocksApi.getHistoricalData(ticker, startStr, endStr),
    staleTime: CACHE_CONFIG.historicalData,
    enabled: enabled && !!ticker,
  });
}

// Hook for fetching company info
export function useCompanyInfo(ticker: string, enabled = true) {
  return useQuery({
    queryKey: stockKeys.company(ticker),
    queryFn: () => stocksApi.getCompanyInfo(ticker),
    staleTime: CACHE_CONFIG.companyInfo,
    enabled: enabled && !!ticker,
  });
}

// Hook for fetching financial metrics
export function useFinancialMetrics(ticker: string, enabled = true) {
  return useQuery({
    queryKey: stockKeys.metrics(ticker),
    queryFn: () => stocksApi.getFinancialMetrics(ticker),
    staleTime: CACHE_CONFIG.companyInfo,
    enabled: enabled && !!ticker,
  });
}

// Hook for stock search
export function useStockSearch(query: string, enabled = true) {
  return useQuery({
    queryKey: stockKeys.search(query),
    queryFn: () => stocksApi.searchStocks(query),
    staleTime: CACHE_CONFIG.companyInfo,
    enabled: enabled && query.length > 0,
  });
}
