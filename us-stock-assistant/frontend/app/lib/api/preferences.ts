import { apiClient } from "../api-client";
import type { UserPreferences, PreferencesUpdateInput } from "@/app/types/preferences";

export const preferencesApi = {
  // Get user preferences
  getPreferences: async (): Promise<UserPreferences> => {
    const response = await apiClient.get("/api/preferences");
    return response.data;
  },

  // Update user preferences
  updatePreferences: async (preferences: PreferencesUpdateInput): Promise<UserPreferences> => {
    const response = await apiClient.put("/api/preferences", preferences);
    return response.data;
  },

  // Reset preferences to defaults
  resetPreferences: async (): Promise<UserPreferences> => {
    const response = await apiClient.post("/api/preferences/reset");
    return response.data;
  },
};
