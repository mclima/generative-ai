"use client";

import { useState, useEffect } from "react";
import { alertsApi } from "@/app/lib/api/alerts";
import { stocksApi } from "@/app/lib/api/stocks";
import type { PriceAlert, PriceAlertInput } from "@/app/types/alerts";
import type { StockSearchResult } from "@/app/types/stocks";
import { handleApiError } from "@/app/lib/api-client";

interface AlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  editAlert?: PriceAlert | null;
}

export default function AlertModal({ isOpen, onClose, onSuccess, editAlert }: AlertModalProps) {
  const [ticker, setTicker] = useState("");
  const [condition, setCondition] = useState<"above" | "below">("above");
  const [targetPrice, setTargetPrice] = useState("");
  const [notificationChannels, setNotificationChannels] = useState<("in-app" | "email" | "push")[]>(["in-app"]);
  const [searchResults, setSearchResults] = useState<StockSearchResult[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Populate form when editing
  useEffect(() => {
    if (editAlert) {
      setTicker(editAlert.ticker);
      setCondition(editAlert.condition);
      setTargetPrice(editAlert.target_price.toString());
      setNotificationChannels(editAlert.notification_channels);
    } else {
      // Reset form for new alert
      setTicker("");
      setCondition("above");
      setTargetPrice("");
      setNotificationChannels(["in-app"]);
    }
    setError(null);
    setValidationErrors({});
  }, [editAlert, isOpen]);

  // Debounced search for ticker
  useEffect(() => {
    if (!ticker || ticker.length < 1 || editAlert) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    const timeoutId = setTimeout(async () => {
      try {
        setIsSearching(true);
        const results = await stocksApi.searchStocks(ticker);
        setSearchResults(results);
        setShowSearchResults(results.length > 0);
      } catch (err) {
        console.error("Search error:", err);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [ticker, editAlert]);

  const handleSelectTicker = (result: StockSearchResult) => {
    setTicker(result.ticker);
    setShowSearchResults(false);
    setSearchResults([]);
  };

  const toggleChannel = (channel: "in-app" | "email" | "push") => {
    setNotificationChannels((prev) => (prev.includes(channel) ? prev.filter((c) => c !== channel) : [...prev, channel]));
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!ticker.trim()) {
      errors.ticker = "Ticker symbol is required";
    } else if (!/^[A-Z]{1,5}$/.test(ticker.trim().toUpperCase())) {
      errors.ticker = "Invalid ticker symbol format";
    }

    const priceNum = parseFloat(targetPrice);
    if (!targetPrice.trim()) {
      errors.targetPrice = "Target price is required";
    } else if (isNaN(priceNum) || priceNum <= 0) {
      errors.targetPrice = "Target price must be a positive number";
    }

    if (notificationChannels.length === 0) {
      errors.channels = "At least one notification channel is required";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) {
      return;
    }

    try {
      setIsSubmitting(true);

      const alertData: PriceAlertInput = {
        ticker: ticker.trim().toUpperCase(),
        condition,
        target_price: parseFloat(targetPrice),
        notification_channels: notificationChannels,
      };

      if (editAlert) {
        await alertsApi.updateAlert(editAlert.id, alertData);
      } else {
        await alertsApi.createAlert(alertData);
      }

      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">{editAlert ? "Edit Price Alert" : "Create Price Alert"}</h2>
            <button onClick={handleClose} disabled={isSubmitting} className="text-gray-400 hover:text-gray-200 disabled:opacity-50">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-900/20 border border-red-800 rounded-lg">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Ticker Search */}
            <div className="relative">
              <label htmlFor="ticker" className="block text-sm font-medium text-gray-300 mb-1">
                Ticker Symbol
              </label>
              <input id="ticker" type="text" value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} disabled={isSubmitting || !!editAlert} className={`w-full px-3 py-2 border rounded-lg bg-[#111111] text-white placeholder-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-[#0a0a0a] disabled:cursor-not-allowed ${validationErrors.ticker ? "border-red-500" : "border-[#2a2a2a]"}`} placeholder="e.g., AAPL" autoComplete="off" />
              {validationErrors.ticker && <p className="mt-1 text-sm text-red-600">{validationErrors.ticker}</p>}

              {/* Search Results Dropdown */}
              {showSearchResults && !editAlert && (
                <div className="absolute z-10 w-full mt-1 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {isSearching ? (
                    <div className="p-3 text-center text-gray-600">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mx-auto"></div>
                    </div>
                  ) : (
                    searchResults.map((result) => (
                      <button key={result.ticker} type="button" onClick={() => handleSelectTicker(result)} className="w-full px-4 py-3 text-left hover:bg-[#222222] border-b border-[#2a2a2a] last:border-b-0">
                        <div className="font-medium text-white">{result.ticker}</div>
                        <div className="text-sm text-gray-400">{result.company_name}</div>
                        <div className="text-xs text-gray-500">{result.exchange}</div>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Condition */}
            <div>
              <label htmlFor="condition" className="block text-sm font-medium text-gray-300 mb-1">
                Alert Condition
              </label>
              <select id="condition" value={condition} onChange={(e) => setCondition(e.target.value as "above" | "below")} disabled={isSubmitting} className="w-full px-3 py-2 border border-[#2a2a2a] bg-[#111111] text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-[#0a0a0a]">
                <option value="above">Price goes above</option>
                <option value="below">Price goes below</option>
              </select>
            </div>

            {/* Target Price */}
            <div>
              <label htmlFor="targetPrice" className="block text-sm font-medium text-gray-300 mb-1">
                Target Price ($)
              </label>
              <input id="targetPrice" type="number" step="0.01" value={targetPrice} onChange={(e) => setTargetPrice(e.target.value)} disabled={isSubmitting} className={`w-full px-3 py-2 border rounded-lg bg-[#111111] text-white placeholder-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-[#0a0a0a] ${validationErrors.targetPrice ? "border-red-500" : "border-[#2a2a2a]"}`} placeholder="e.g., 150.00" />
              {validationErrors.targetPrice && <p className="mt-1 text-sm text-red-600">{validationErrors.targetPrice}</p>}
            </div>

            {/* Notification Channels */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Notification Channels</label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input type="checkbox" checked={notificationChannels.includes("in-app")} onChange={() => toggleChannel("in-app")} disabled={isSubmitting} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50" />
                  <span className="ml-2 text-sm text-gray-300">In-App Notifications</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" checked={notificationChannels.includes("email")} onChange={() => toggleChannel("email")} disabled={isSubmitting} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50" />
                  <span className="ml-2 text-sm text-gray-300">Email Notifications</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" checked={notificationChannels.includes("push")} onChange={() => toggleChannel("push")} disabled={isSubmitting} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50" />
                  <span className="ml-2 text-sm text-gray-300">Push Notifications</span>
                </label>
              </div>
              {validationErrors.channels && <p className="mt-1 text-sm text-red-600">{validationErrors.channels}</p>}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <button type="button" onClick={handleClose} disabled={isSubmitting} className="flex-1 px-4 py-2 border border-[#2a2a2a] text-gray-300 rounded-lg hover:bg-[#2a2a2a] disabled:opacity-50 disabled:cursor-not-allowed">
                Cancel
              </button>
              <button type="submit" disabled={isSubmitting} className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {editAlert ? "Updating..." : "Creating..."}
                  </>
                ) : (
                  <>{editAlert ? "Update Alert" : "Create Alert"}</>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
