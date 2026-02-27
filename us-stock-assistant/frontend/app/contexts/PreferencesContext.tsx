"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { preferencesApi } from "@/app/lib/api";
import type { UserPreferences } from "@/app/types/preferences";

interface PreferencesContextType {
  preferences: UserPreferences | null;
  loading: boolean;
  error: string | null;
  refreshPreferences: () => Promise<void>;
}

const PreferencesContext = createContext<PreferencesContextType | undefined>(undefined);

const DEFAULT_PREFERENCES: UserPreferences = {
  default_chart_type: "line",
  default_time_range: "1M",
  preferred_news_sources: [],
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

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await preferencesApi.getPreferences();
      setPreferences(data);
    } catch (err) {
      console.error("Error loading preferences:", err);
      setError("Failed to load preferences");
      // Use default preferences if loading fails
      setPreferences(DEFAULT_PREFERENCES);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPreferences();
  }, []);

  const refreshPreferences = async () => {
    await loadPreferences();
  };

  return (
    <PreferencesContext.Provider
      value={{
        preferences,
        loading,
        error,
        refreshPreferences,
      }}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences() {
  const context = useContext(PreferencesContext);
  if (context === undefined) {
    throw new Error("usePreferences must be used within a PreferencesProvider");
  }
  return context;
}
