"use client";

import { useState, useEffect } from "react";
import { preferencesApi, complianceApi } from "@/app/lib/api";
import { usePreferences } from "@/app/contexts/PreferencesContext";
import type { UserPreferences, NotificationSettings } from "@/app/types/preferences";
import type { DeletionStatus } from "@/app/lib/api/compliance";

const NEWS_SOURCES = ["Bloomberg", "Reuters", "CNBC", "Wall Street Journal", "Financial Times", "MarketWatch", "Seeking Alpha", "Yahoo Finance"];

export default function SettingsPage() {
  const { refreshPreferences } = usePreferences();
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [deletionStatus, setDeletionStatus] = useState<DeletionStatus | null>(null);
  const [exportingData, setExportingData] = useState(false);
  const [deletingAccount, setDeletingAccount] = useState(false);

  useEffect(() => {
    loadPreferences();
    loadDeletionStatus();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await preferencesApi.getPreferences();
      setPreferences(data);
    } catch (err) {
      setError("Failed to load preferences. Please try again.");
      console.error("Error loading preferences:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadDeletionStatus = async () => {
    try {
      const status = await complianceApi.getDeletionStatus();
      setDeletionStatus(status);
    } catch (err) {
      console.error("Error loading deletion status:", err);
    }
  };

  const handleSave = async () => {
    if (!preferences) return;

    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);
      await preferencesApi.updatePreferences(preferences);
      await refreshPreferences();
      setSuccessMessage("Preferences saved successfully!");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError("Failed to save preferences. Please try again.");
      console.error("Error saving preferences:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Are you sure you want to reset all preferences to defaults?")) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);
      const data = await preferencesApi.resetPreferences();
      setPreferences(data);
      setSuccessMessage("Preferences reset to defaults!");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError("Failed to reset preferences. Please try again.");
      console.error("Error resetting preferences:", err);
    } finally {
      setSaving(false);
    }
  };

  const updatePreference = <K extends keyof UserPreferences>(key: K, value: UserPreferences[K]) => {
    if (!preferences) return;
    setPreferences({ ...preferences, [key]: value });
  };

  const updateNotificationSetting = <K extends keyof NotificationSettings>(key: K, value: NotificationSettings[K]) => {
    if (!preferences) return;
    setPreferences({
      ...preferences,
      notification_settings: {
        ...preferences.notification_settings,
        [key]: value,
      },
    });
  };

  const updateAlertType = (alertType: keyof NotificationSettings["alert_types"], value: boolean) => {
    if (!preferences) return;
    setPreferences({
      ...preferences,
      notification_settings: {
        ...preferences.notification_settings,
        alert_types: {
          ...preferences.notification_settings.alert_types,
          [alertType]: value,
        },
      },
    });
  };

  const toggleNewsSource = (source: string) => {
    if (!preferences) return;
    const sources = preferences.preferred_news_sources;
    const newSources = sources.includes(source) ? sources.filter((s) => s !== source) : [...sources, source];
    updatePreference("preferred_news_sources", newSources);
  };

  const handleExportData = async () => {
    try {
      setExportingData(true);
      setError(null);
      await complianceApi.downloadData();
      setSuccessMessage("Your data has been downloaded successfully!");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError("Failed to export data. Please try again.");
      console.error("Error exporting data:", err);
    } finally {
      setExportingData(false);
    }
  };

  const handleRequestDeletion = async () => {
    if (!confirm("Are you sure you want to delete your account? This action will permanently delete all your data in 30 days. You can cancel this request before the deletion date.")) {
      return;
    }

    try {
      setDeletingAccount(true);
      setError(null);
      const result = await complianceApi.requestDeletion();
      setSuccessMessage(`Account deletion scheduled for ${new Date(result.scheduled_deletion_date).toLocaleDateString()}`);
      await loadDeletionStatus();
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      setError("Failed to request account deletion. Please try again.");
      console.error("Error requesting deletion:", err);
    } finally {
      setDeletingAccount(false);
    }
  };

  const handleCancelDeletion = async () => {
    if (!confirm("Are you sure you want to cancel the account deletion request?")) {
      return;
    }

    try {
      setDeletingAccount(true);
      setError(null);
      await complianceApi.cancelDeletion();
      setSuccessMessage("Account deletion cancelled successfully!");
      await loadDeletionStatus();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError("Failed to cancel deletion. Please try again.");
      console.error("Error cancelling deletion:", err);
    } finally {
      setDeletingAccount(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-400">Loading preferences...</div>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-red-600">Failed to load preferences</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-white">Settings</h1>

      <div className="space-y-8">
        {/* Chart Preferences */}
        <section className="bg-[#1a1a1a] border border-[#2a2a2a] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-white">Chart Preferences</h2>

          <div className="space-y-4">
            <div>
              <label htmlFor="chart-type" className="block text-sm font-medium text-gray-300 mb-2">
                Default Chart Type
              </label>
              <select id="chart-type" value={preferences.default_chart_type} onChange={(e) => updatePreference("default_chart_type", e.target.value as "line" | "candlestick")} className="w-full px-3 py-2 border border-[#2a2a2a] bg-[#111111] text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="line">Line Chart</option>
                <option value="candlestick">Candlestick Chart</option>
              </select>
            </div>

            <div>
              <label htmlFor="time-range" className="block text-sm font-medium text-gray-300 mb-2">
                Default Time Range
              </label>
              <select id="time-range" value={preferences.default_time_range} onChange={(e) => updatePreference("default_time_range", e.target.value as UserPreferences["default_time_range"])} className="w-full px-3 py-2 border border-[#2a2a2a] bg-[#111111] text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="1D">1 Day</option>
                <option value="1W">1 Week</option>
                <option value="1M">1 Month</option>
                <option value="3M">3 Months</option>
                <option value="1Y">1 Year</option>
                <option value="ALL">All Time</option>
              </select>
            </div>
          </div>
        </section>

        {/* News Preferences */}
        <section className="bg-[#1a1a1a] border border-[#2a2a2a] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-white">News Preferences</h2>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Preferred News Sources</label>
            <div className="grid grid-cols-2 gap-3">
              {NEWS_SOURCES.map((source) => (
                <label key={source} className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" checked={preferences.preferred_news_sources.includes(source)} onChange={() => toggleNewsSource(source)} className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">{source}</span>
                </label>
              ))}
            </div>
          </div>
        </section>

        {/* Notification Preferences */}
        <section className="bg-[#1a1a1a] border border-[#2a2a2a] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-white">Notification Preferences</h2>

          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-3">Notification Channels</h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" checked={preferences.notification_settings.in_app} onChange={(e) => updateNotificationSetting("in_app", e.target.checked)} className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">In-App Notifications</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" checked={preferences.notification_settings.email} onChange={(e) => updateNotificationSetting("email", e.target.checked)} className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">Email Notifications</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" checked={preferences.notification_settings.push} onChange={(e) => updateNotificationSetting("push", e.target.checked)} className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">Push Notifications</span>
                </label>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-3">Alert Types</h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" checked={preferences.notification_settings.alert_types.price_alerts} onChange={(e) => updateAlertType("price_alerts", e.target.checked)} className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">Price Alerts</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" checked={preferences.notification_settings.alert_types.news_updates} onChange={(e) => updateAlertType("news_updates", e.target.checked)} className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">News Updates</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input type="checkbox" checked={preferences.notification_settings.alert_types.portfolio_changes} onChange={(e) => updateAlertType("portfolio_changes", e.target.checked)} className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">Portfolio Changes</span>
                </label>
              </div>
            </div>
          </div>
        </section>

        {/* Data Refresh Preferences */}
        <section className="bg-[#1a1a1a] border border-[#2a2a2a] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-white">Data Refresh</h2>

          <div>
            <label htmlFor="refresh-interval" className="block text-sm font-medium text-gray-300 mb-2">
              Refresh Interval (seconds)
            </label>
            <div className="flex items-center space-x-4">
              <input id="refresh-interval" type="range" min="15" max="300" step="15" value={preferences.refresh_interval} onChange={(e) => updatePreference("refresh_interval", parseInt(e.target.value))} className="flex-1 h-2 bg-[#2a2a2a] rounded-lg appearance-none cursor-pointer" />
              <span className="text-sm font-medium text-gray-300 w-16 text-right">{preferences.refresh_interval}s</span>
            </div>
            <p className="mt-2 text-xs text-gray-500">How often to refresh stock prices and market data (15-300 seconds)</p>
          </div>
        </section>

        {/* Data Privacy & Compliance */}
        <section className="bg-[#1a1a1a] border border-[#2a2a2a] p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-white">Data Privacy &amp; Compliance</h2>

          <div className="space-y-6">
            {/* Data Export */}
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-2">Download Your Data</h3>
              <p className="text-sm text-gray-400 mb-3">Export all your personal data including portfolio, alerts, preferences, and notifications in JSON format (GDPR/CCPA compliance).</p>
              <button onClick={handleExportData} disabled={exportingData} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm">
                {exportingData ? "Exporting..." : "Download My Data"}
              </button>
            </div>

            {/* Account Deletion */}
            <div className="pt-6 border-t border-[#2a2a2a]">
              <h3 className="text-sm font-medium text-gray-300 mb-2">Delete Account</h3>

              {deletionStatus?.has_pending_deletion ? (
                <div className="bg-yellow-900/20 border border-yellow-700 rounded-md p-4 mb-3">
                  <p className="text-sm text-yellow-400 mb-2">
                    <strong>Account deletion scheduled</strong>
                  </p>
                  <p className="text-sm text-yellow-400 mb-3">
                    Your account and all associated data will be permanently deleted on <strong>{new Date(deletionStatus.scheduled_deletion_date!).toLocaleDateString()}</strong>.
                  </p>
                  <button onClick={handleCancelDeletion} disabled={deletingAccount} className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm">
                    {deletingAccount ? "Cancelling..." : "Cancel Deletion"}
                  </button>
                </div>
              ) : (
                <>
                  <p className="text-sm text-gray-400 mb-3">Permanently delete your account and all associated data. This action will be scheduled for 30 days from now, giving you time to cancel if needed.</p>
                  <button onClick={handleRequestDeletion} disabled={deletingAccount} className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm">
                    {deletingAccount ? "Processing..." : "Delete Account"}
                  </button>
                </>
              )}
            </div>
          </div>
        </section>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4">
          <button onClick={handleReset} disabled={saving} className="px-6 py-2 border border-[#2a2a2a] rounded-md text-gray-300 hover:bg-[#2a2a2a] disabled:opacity-50 disabled:cursor-not-allowed">
            Reset to Defaults
          </button>
          <button onClick={handleSave} disabled={saving} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
            {saving ? "Saving..." : "Save Preferences"}
          </button>
        </div>
        {error && <div className="p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-400">{error}</div>}
        {successMessage && <div className="p-4 bg-green-900/20 border border-green-800 rounded-lg text-green-400">{successMessage}</div>}
      </div>
    </div>
  );
}
