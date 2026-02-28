import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CACHE_CONFIG } from "../providers/QueryProvider";
import { portfolioApi } from "../lib/api/portfolio";
import { Portfolio, StockPosition, StockPositionInput, PortfolioMetrics } from "../types/portfolio";

// Query keys for cache management
export const portfolioKeys = {
  all: ["portfolio"] as const,
  detail: (userId: string) => [...portfolioKeys.all, userId] as const,
  metrics: (userId: string) => [...portfolioKeys.all, "metrics", userId] as const,
};

// Hook for fetching portfolio
export function usePortfolio(userId: string, enabled = true) {
  return useQuery({
    queryKey: portfolioKeys.detail(userId),
    queryFn: () => portfolioApi.getPortfolio(userId),
    staleTime: CACHE_CONFIG.portfolio,
    enabled: enabled && !!userId,
  });
}

// Hook for fetching portfolio metrics
export function usePortfolioMetrics(userId: string, enabled = true) {
  return useQuery({
    queryKey: portfolioKeys.metrics(userId),
    queryFn: () => portfolioApi.calculateMetrics(userId),
    staleTime: CACHE_CONFIG.portfolio,
    enabled: enabled && !!userId,
  });
}

// Hook for adding a stock position with optimistic updates
export function useAddPosition(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (position: StockPositionInput) => portfolioApi.addPosition(userId, position),
    // Optimistic update
    onMutate: async (newPosition) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: portfolioKeys.detail(userId) });

      // Snapshot previous value
      const previousPortfolio = queryClient.getQueryData<Portfolio>(portfolioKeys.detail(userId));

      // Optimistically update
      if (previousPortfolio) {
        queryClient.setQueryData<Portfolio>(portfolioKeys.detail(userId), {
          ...previousPortfolio,
          positions: [
            ...previousPortfolio.positions,
            {
              ...newPosition,
              id: "temp-" + Date.now(),
              currentPrice: 0,
              currentValue: 0,
              gainLoss: 0,
              gainLossPercent: 0,
            } as StockPosition,
          ],
        });
      }

      return { previousPortfolio };
    },
    // On error, rollback
    onError: (err, newPosition, context) => {
      if (context?.previousPortfolio) {
        queryClient.setQueryData(portfolioKeys.detail(userId), context.previousPortfolio);
      }
    },
    // Always refetch after error or success
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(userId) });
      queryClient.invalidateQueries({ queryKey: portfolioKeys.metrics(userId) });
    },
  });
}

// Hook for updating a stock position with optimistic updates
export function useUpdatePosition(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ positionId, updates }: { positionId: string; updates: Partial<StockPositionInput> }) => portfolioApi.updatePosition(userId, positionId, updates),
    // Optimistic update
    onMutate: async ({ positionId, updates }) => {
      await queryClient.cancelQueries({ queryKey: portfolioKeys.detail(userId) });

      const previousPortfolio = queryClient.getQueryData<Portfolio>(portfolioKeys.detail(userId));

      if (previousPortfolio) {
        queryClient.setQueryData<Portfolio>(portfolioKeys.detail(userId), {
          ...previousPortfolio,
          positions: previousPortfolio.positions.map((pos) => (pos.id === positionId ? { ...pos, ...updates } : pos)),
        });
      }

      return { previousPortfolio };
    },
    onError: (err, variables, context) => {
      if (context?.previousPortfolio) {
        queryClient.setQueryData(portfolioKeys.detail(userId), context.previousPortfolio);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(userId) });
      queryClient.invalidateQueries({ queryKey: portfolioKeys.metrics(userId) });
    },
  });
}

// Hook for removing a stock position with optimistic updates
export function useRemovePosition(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (positionId: string) => portfolioApi.removePosition(userId, positionId),
    // Optimistic update
    onMutate: async (positionId) => {
      await queryClient.cancelQueries({ queryKey: portfolioKeys.detail(userId) });

      const previousPortfolio = queryClient.getQueryData<Portfolio>(portfolioKeys.detail(userId));

      if (previousPortfolio) {
        queryClient.setQueryData<Portfolio>(portfolioKeys.detail(userId), {
          ...previousPortfolio,
          positions: previousPortfolio.positions.filter((pos) => pos.id !== positionId),
        });
      }

      return { previousPortfolio };
    },
    onError: (err, positionId, context) => {
      if (context?.previousPortfolio) {
        queryClient.setQueryData(portfolioKeys.detail(userId), context.previousPortfolio);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(userId) });
      queryClient.invalidateQueries({ queryKey: portfolioKeys.metrics(userId) });
    },
  });
}

// Hook for exporting portfolio
export function useExportPortfolio(userId: string) {
  return useMutation({
    mutationFn: (format: "csv" | "excel") => portfolioApi.exportPortfolio(userId, format),
  });
}

// Hook for importing portfolio
export function useImportPortfolio(userId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, format }: { file: File; format: "csv" | "excel" }) => portfolioApi.importPortfolio(userId, file, format),
    onSuccess: () => {
      // Invalidate portfolio queries after import
      queryClient.invalidateQueries({ queryKey: portfolioKeys.detail(userId) });
      queryClient.invalidateQueries({ queryKey: portfolioKeys.metrics(userId) });
    },
  });
}
