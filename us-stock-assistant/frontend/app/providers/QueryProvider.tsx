"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";

// Configure cache TTLs matching backend requirements
const CACHE_CONFIG = {
  // Stock prices: 60 seconds (Requirement 3.3)
  stockPrice: 60 * 1000,
  // News: 15 minutes (Requirement 11.7)
  news: 15 * 60 * 1000,
  // Market overview: 15 minutes (Requirement 12.5)
  marketOverview: 15 * 60 * 1000,
  // Historical data: 1 hour
  historicalData: 60 * 60 * 1000,
  // Portfolio data: 2 seconds (Requirement 7.1)
  portfolio: 2 * 1000,
  // Company info: 24 hours (rarely changes)
  companyInfo: 24 * 60 * 60 * 1000,
};

export { CACHE_CONFIG };

export default function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Default stale time: 5 minutes
            staleTime: 5 * 60 * 1000,
            // Keep unused data in cache for 10 minutes
            gcTime: 10 * 60 * 1000,
            // Retry failed requests
            retry: 2,
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
            // Refetch on window focus for real-time data
            refetchOnWindowFocus: true,
            // Don't refetch on mount if data is fresh
            refetchOnMount: false,
          },
          mutations: {
            // Retry mutations once
            retry: 1,
            retryDelay: 1000,
          },
        },
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
