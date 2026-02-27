import { apiClient } from "../api-client";
import type { PriceAlert, PriceAlertInput } from "@/app/types/alerts";

export const alertsApi = {
  // Get all user alerts
  async getAlerts(): Promise<PriceAlert[]> {
    const response = await apiClient.get("/api/alerts");
    return response.data;
  },

  // Create a new price alert
  async createAlert(alert: PriceAlertInput): Promise<PriceAlert> {
    const response = await apiClient.post("/api/alerts", alert);
    return response.data;
  },

  // Update an existing alert
  async updateAlert(id: string, alert: Partial<PriceAlertInput>): Promise<PriceAlert> {
    const response = await apiClient.put(`/api/alerts/${id}`, alert);
    return response.data;
  },

  // Delete an alert
  async deleteAlert(id: string): Promise<void> {
    await apiClient.delete(`/api/alerts/${id}`);
  },
};
