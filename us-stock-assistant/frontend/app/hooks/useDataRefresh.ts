import { useEffect, useRef } from "react";
import { usePreferences } from "@/app/contexts/PreferencesContext";

/**
 * Hook to automatically refresh data based on user's refresh interval preference
 * @param callback Function to call on each refresh
 * @param enabled Whether the refresh is enabled (default: true)
 */
export function useDataRefresh(callback: () => void, enabled: boolean = true) {
  const { preferences } = usePreferences();
  const callbackRef = useRef(callback);

  // Update callback ref when it changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled || !preferences) {
      return;
    }

    const intervalMs = preferences.refresh_interval * 1000;

    const intervalId = setInterval(() => {
      callbackRef.current();
    }, intervalMs);

    return () => clearInterval(intervalId);
  }, [preferences, enabled]);
}
