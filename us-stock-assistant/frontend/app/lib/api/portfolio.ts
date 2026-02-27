import { apiClient } from "../api-client";
import type { Portfolio, StockPosition, StockPositionInput, PortfolioMetrics } from "@/app/types/portfolio";

export const portfolioApi = {
  // Get user's portfolio
  getPortfolio: async (): Promise<Portfolio> => {
    const response = await apiClient.get("/api/portfolio");
    return response.data;
  },

  // Add a stock position
  addPosition: async (position: StockPositionInput): Promise<StockPosition> => {
    const response = await apiClient.post("/api/portfolio/positions", position);
    return response.data;
  },

  // Update a stock position
  updatePosition: async (positionId: string, updates: Partial<StockPositionInput>): Promise<StockPosition> => {
    const response = await apiClient.put(`/api/portfolio/positions/${positionId}`, updates);
    return response.data;
  },

  // Remove a stock position
  removePosition: async (positionId: string): Promise<void> => {
    await apiClient.delete(`/api/portfolio/positions/${positionId}`);
  },

  // Get portfolio metrics
  getMetrics: async (): Promise<PortfolioMetrics> => {
    const response = await apiClient.get("/api/portfolio/metrics");
    return response.data;
  },

  // Export portfolio
  exportPortfolio: async (format: "csv" | "excel"): Promise<Blob> => {
    const response = await apiClient.get(`/api/portfolio/export?format=${format}`, {
      responseType: "blob",
    });
    return response.data;
  },

  // Import portfolio
  importPortfolio: async (file: File, format: "csv" | "excel"): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("format", format);

    const response = await apiClient.post("/api/portfolio/import", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },
};
