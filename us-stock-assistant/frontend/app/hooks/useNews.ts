import { useQuery } from "@tanstack/react-query";
import { CACHE_CONFIG } from "../providers/QueryProvider";
import * as newsApi from "../lib/api/news";

// Query keys for cache management
export const newsKeys = {
  all: ["news"] as const,
  stock: (ticker: string, limit: number) => [...newsKeys.all, "stock", ticker, limit] as const,
  market: (limit: number) => [...newsKeys.all, "market", limit] as const,
  sentiment: (ticker: string) => [...newsKeys.all, "sentiment", ticker] as const,
  batch: (tickers: string[]) => [...newsKeys.all, "batch", tickers.sort().join(",")] as const,
};

// Hook for fetching stock news
export function useStockNews(ticker: string, limit = 10, enabled = true) {
  return useQuery({
    queryKey: newsKeys.stock(ticker, limit),
    queryFn: () => newsApi.getStockNews(ticker, limit),
    staleTime: CACHE_CONFIG.news,
    enabled: enabled && !!ticker,
  });
}

// Hook for fetching market news
export function useMarketNews(limit = 20, enabled = true) {
  return useQuery({
    queryKey: newsKeys.market(limit),
    queryFn: () => newsApi.getMarketNews(limit),
    staleTime: CACHE_CONFIG.news,
    enabled,
  });
}

// Hook for fetching stock sentiment
export function useStockSentiment(ticker: string, enabled = true) {
  return useQuery({
    queryKey: newsKeys.sentiment(ticker),
    queryFn: () => newsApi.getStockSentiment(ticker),
    staleTime: CACHE_CONFIG.news,
    enabled: enabled && !!ticker,
  });
}

// Hook for fetching news for multiple stocks
export function useBatchStockNews(tickers: string[], enabled = true) {
  return useQuery({
    queryKey: newsKeys.batch(tickers),
    queryFn: () => newsApi.getBatchStockNews(tickers),
    staleTime: CACHE_CONFIG.news,
    enabled: enabled && tickers.length > 0,
  });
}
