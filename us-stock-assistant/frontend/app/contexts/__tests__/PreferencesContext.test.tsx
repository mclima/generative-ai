import { renderHook, waitFor } from "@testing-library/react";
import { PreferencesProvider, usePreferences } from "../PreferencesContext";
import { preferencesApi } from "@/app/lib/api";
import { ReactNode } from "react";

// Mock the API
jest.mock("@/app/lib/api", () => ({
  preferencesApi: {
    getPreferences: jest.fn(),
  },
}));

const mockPreferences = {
  default_chart_type: "line" as const,
  default_time_range: "1M" as const,
  preferred_news_sources: ["Bloomberg", "Reuters"],
  notification_settings: {
    in_app: true,
    email: false,
    push: false,
    alert_types: {
      price_alerts: true,
      news_updates: true,
      portfolio_changes: true,
    },
  },
  refresh_interval: 60,
};

describe("PreferencesContext", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const wrapper = ({ children }: { children: ReactNode }) => <PreferencesProvider>{children}</PreferencesProvider>;

  describe("Loading Preferences", () => {
    it("should load preferences on mount", async () => {
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);

      const { result } = renderHook(() => usePreferences(), { wrapper });

      expect(result.current.loading).toBe(true);
      expect(result.current.preferences).toBeNull();

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.preferences).toEqual(mockPreferences);
      expect(result.current.error).toBeNull();
    });

    it("should use default preferences when loading fails", async () => {
      (preferencesApi.getPreferences as jest.Mock).mockRejectedValue(new Error("Failed to load"));

      const { result } = renderHook(() => usePreferences(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.preferences).toBeDefined();
      expect(result.current.preferences?.default_chart_type).toBe("line");
      expect(result.current.preferences?.default_time_range).toBe("1M");
      expect(result.current.preferences?.refresh_interval).toBe(60);
      expect(result.current.error).toBe("Failed to load preferences");
    });

    it("should set error state when loading fails", async () => {
      (preferencesApi.getPreferences as jest.Mock).mockRejectedValue(new Error("Network error"));

      const { result } = renderHook(() => usePreferences(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe("Failed to load preferences");
    });
  });

  describe("Refresh Preferences", () => {
    it("should refresh preferences when refreshPreferences is called", async () => {
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);

      const { result } = renderHook(() => usePreferences(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(preferencesApi.getPreferences).toHaveBeenCalledTimes(1);

      // Update mock to return different preferences
      const updatedPreferences = {
        ...mockPreferences,
        default_chart_type: "candlestick" as const,
      };
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(updatedPreferences);

      // Refresh preferences
      await result.current.refreshPreferences();

      await waitFor(() => {
        expect(result.current.preferences?.default_chart_type).toBe("candlestick");
      });

      expect(preferencesApi.getPreferences).toHaveBeenCalledTimes(2);
    });

    it("should handle errors during refresh", async () => {
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);

      const { result } = renderHook(() => usePreferences(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Make refresh fail
      (preferencesApi.getPreferences as jest.Mock).mockRejectedValue(new Error("Refresh failed"));

      await result.current.refreshPreferences();

      await waitFor(() => {
        expect(result.current.error).toBe("Failed to load preferences");
      });
    });
  });

  describe("Context Usage", () => {
    it("should throw error when used outside provider", () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, "error").mockImplementation(() => {});

      expect(() => {
        renderHook(() => usePreferences());
      }).toThrow("usePreferences must be used within a PreferencesProvider");

      consoleSpy.mockRestore();
    });
  });

  describe("Default Preferences", () => {
    it("should provide correct default preferences structure", async () => {
      (preferencesApi.getPreferences as jest.Mock).mockRejectedValue(new Error("Failed"));

      const { result } = renderHook(() => usePreferences(), { wrapper });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const prefs = result.current.preferences;
      expect(prefs).toBeDefined();
      expect(prefs?.default_chart_type).toBe("line");
      expect(prefs?.default_time_range).toBe("1M");
      expect(prefs?.preferred_news_sources).toEqual([]);
      expect(prefs?.notification_settings.in_app).toBe(true);
      expect(prefs?.notification_settings.email).toBe(false);
      expect(prefs?.notification_settings.push).toBe(false);
      expect(prefs?.notification_settings.alert_types.price_alerts).toBe(true);
      expect(prefs?.notification_settings.alert_types.news_updates).toBe(true);
      expect(prefs?.notification_settings.alert_types.portfolio_changes).toBe(true);
      expect(prefs?.refresh_interval).toBe(60);
    });
  });
});
