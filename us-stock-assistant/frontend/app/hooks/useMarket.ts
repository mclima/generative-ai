import { useQuery } from "@tanstack/react-query";
import { CACHE_CONFIG } from "../providers/QueryProvider";
import { marketApi } from "../lib/api/market";

// Query keys for cache management
export const marketKeys = {
  all: ["market"] as const,
  overview: () => [...marketKeys.all, "overview"] as const,
  trending: (limit: number) => [...marketKeys.all, "trending", limit] as const,
  sectors: () => [...marketKeys.all, "sectors"] as const,
  indices: () => [...marketKeys.all, "indices"] as const,
};

// Hook for fetching market overview
export function useMarketOverview(enabled = true) {
  return useQuery({
    queryKey: marketKeys.overview(),
    queryFn: () => marketApi.getMarketOverview(),
    staleTime: CACHE_CONFIG.marketOverview,
    enabled,
  });
}

// Hook for fetching trending tickers
export function useTrendingTickers(limit = 10, enabled = true) {
  return useQuery({
    queryKey: marketKeys.trending(limit),
    queryFn: () => marketApi.getTrendingTickers(limit),
    staleTime: CACHE_CONFIG.marketOverview,
    enabled,
  });
}

// Hook for fetching sector performance
export function useSectorPerformance(enabled = true) {
  return useQuery({
    queryKey: marketKeys.sectors(),
    queryFn: () => marketApi.getSectorPerformance(),
    staleTime: CACHE_CONFIG.marketOverview,
    enabled,
  });
}

// Hook for fetching market indices
export function useMarketIndices(enabled = true) {
  return useQuery({
    queryKey: marketKeys.indices(),
    queryFn: () => marketApi.getMarketIndices(),
    staleTime: CACHE_CONFIG.marketOverview,
    enabled,
  });
}
