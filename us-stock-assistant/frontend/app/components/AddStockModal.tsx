"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { stocksApi } from "@/app/lib/api/stocks";
import { portfolioApi } from "@/app/lib/api/portfolio";
import type { StockPositionInput, StockPosition } from "@/app/types/portfolio";
import type { StockSearchResult } from "@/app/types/stocks";
import { handleApiError } from "@/app/lib/api-client";

interface AddStockModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  onSubmit?: (position: StockPositionInput) => Promise<void>;
  isSubmitting?: boolean;
  editPosition?: StockPosition | null;
  initialTicker?: string;
}

export default function AddStockModal({ isOpen, onClose, onSuccess, onSubmit, isSubmitting: externalIsSubmitting, editPosition, initialTicker }: AddStockModalProps) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [purchasePrice, setPurchasePrice] = useState("");
  const [purchaseDate, setPurchaseDate] = useState("");
  const [searchResults, setSearchResults] = useState<StockSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [internalIsSubmitting, setInternalIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const isSubmitting = externalIsSubmitting ?? internalIsSubmitting;
  const tickerRef = useRef<HTMLDivElement>(null);

  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (tickerRef.current && !tickerRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Populate form when editing or with initial ticker
  useEffect(() => {
    if (editPosition) {
      setTicker(editPosition.ticker);
      setQuantity(editPosition.quantity.toString());
      setPurchasePrice(editPosition.purchase_price.toString());
      setPurchaseDate(editPosition.purchase_date);
    } else if (initialTicker) {
      setTicker(initialTicker);
      setQuantity("");
      setPurchasePrice("");
      setPurchaseDate("");
    } else {
      // Reset form for new position
      setTicker("");
      setQuantity("");
      setPurchasePrice("");
      setPurchaseDate("");
    }
    setError(null);
    setValidationErrors({});
  }, [editPosition, initialTicker, isOpen]);

  // Debounced search for ticker
  useEffect(() => {
    if (!ticker || ticker.trim().length === 0 || editPosition) {
      setSearchResults([]);
      setIsSearching(false);
      setDropdownOpen(false);
      return;
    }

    console.log(`Ticker changed to: "${ticker}", setting isSearching=true, dropdownOpen=true`);
    setIsSearching(true);
    setDropdownOpen(true);

    const timeoutId = setTimeout(async () => {
      console.log(`Searching for: "${ticker}"`);
      try {
        const results = await stocksApi.searchStocks(ticker);
        console.log(`Search results for "${ticker}":`, results.length, 'results');
        setSearchResults(results);
        setIsSearching(false);
        // Keep dropdown open even if no results to show "No results found"
        setDropdownOpen(true);
      } catch (err) {
        console.error("Search error:", err);
        setSearchResults([]);
        setIsSearching(false);
        setDropdownOpen(false);
      }
    }, 300);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [ticker, editPosition]);

  const handleSelectTicker = (result: StockSearchResult) => {
    setTicker(result.ticker);
    setDropdownOpen(false);
    setSearchResults([]);
    setIsSearching(false);
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!ticker.trim()) {
      errors.ticker = "Ticker symbol is required";
    } else if (!/^[A-Z]{1,5}$/.test(ticker.trim().toUpperCase())) {
      errors.ticker = "Invalid ticker symbol format";
    }

    const quantityNum = parseFloat(quantity);
    if (!quantity.trim()) {
      errors.quantity = "Quantity is required";
    } else if (isNaN(quantityNum) || quantityNum <= 0) {
      errors.quantity = "Quantity must be a positive number";
    }

    const priceNum = parseFloat(purchasePrice);
    if (!purchasePrice.trim()) {
      errors.purchasePrice = "Purchase price is required";
    } else if (isNaN(priceNum) || priceNum <= 0) {
      errors.purchasePrice = "Purchase price must be a positive number";
    }

    if (!purchaseDate.trim()) {
      errors.purchaseDate = "Purchase date is required";
    } else {
      const date = new Date(purchaseDate);
      const today = new Date();
      if (date > today) {
        errors.purchaseDate = "Purchase date cannot be in the future";
      }
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
      setInternalIsSubmitting(true);

      const positionData: StockPositionInput = {
        ticker: ticker.trim().toUpperCase(),
        quantity: parseFloat(quantity),
        purchase_price: parseFloat(purchasePrice),
        purchase_date: purchaseDate,
      };

      // Use custom onSubmit if provided, otherwise use default API calls
      if (onSubmit) {
        await onSubmit(positionData);
      } else {
        if (editPosition) {
          await portfolioApi.updatePosition(editPosition.id, positionData);
        } else {
          await portfolioApi.addPosition(positionData);
        }
      }

      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setInternalIsSubmitting(false);
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
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-visible">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">{editPosition ? "Edit Position" : "Add Stock Position"}</h2>
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
            <div className="relative" ref={tickerRef}>
              <label htmlFor="ticker" className="block text-sm font-medium text-gray-300 mb-1">
                Ticker Symbol
              </label>
              <input id="ticker" type="text" value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} disabled={isSubmitting || !!editPosition} className={`w-full px-3 py-2 border rounded-lg bg-[#111111] text-white placeholder-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-[#0a0a0a] disabled:cursor-not-allowed ${validationErrors.ticker ? "border-red-500" : "border-[#2a2a2a]"}`} placeholder="e.g., AAPL" autoComplete="off" />
              {validationErrors.ticker && <p className="mt-1 text-sm text-red-600">{validationErrors.ticker}</p>}

              {/* Search Results Dropdown */}
              {dropdownOpen && !editPosition && (
                <div className="absolute z-[200] w-full mt-1 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {isSearching ? (
                    <div className="p-3 text-center text-gray-600">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mx-auto"></div>
                    </div>
                  ) : searchResults.length > 0 ? (
                    searchResults.map((result) => (
                      <button key={result.ticker} type="button" onClick={() => handleSelectTicker(result)} className="w-full px-4 py-3 text-left hover:bg-[#222222] border-b border-[#2a2a2a] last:border-b-0">
                        <div className="font-medium text-white">{result.ticker}</div>
                        <div className="text-sm text-gray-400">{result.company_name}</div>
                        <div className="text-xs text-gray-500">{result.exchange}</div>
                      </button>
                    ))
                  ) : (
                    <div className="p-4 text-center text-gray-500">
                      <p className="text-sm">No stocks found</p>
                      <p className="text-xs text-gray-600 mt-1">Try a different search term</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Quantity */}
            <div>
              <label htmlFor="quantity" className="block text-sm font-medium text-gray-300 mb-1">
                Quantity
              </label>
              <input id="quantity" type="number" step="0.0001" value={quantity} onChange={(e) => setQuantity(e.target.value)} disabled={isSubmitting} className={`w-full px-3 py-2 border rounded-lg bg-[#111111] text-white placeholder-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-[#0a0a0a] ${validationErrors.quantity ? "border-red-500" : "border-[#2a2a2a]"}`} placeholder="e.g., 10" />
              {validationErrors.quantity && <p className="mt-1 text-sm text-red-600">{validationErrors.quantity}</p>}
            </div>

            {/* Purchase Price */}
            <div>
              <label htmlFor="purchasePrice" className="block text-sm font-medium text-gray-300 mb-1">
                Purchase Price ($)
              </label>
              <input id="purchasePrice" type="number" step="0.01" value={purchasePrice} onChange={(e) => setPurchasePrice(e.target.value)} disabled={isSubmitting} className={`w-full px-3 py-2 border rounded-lg bg-[#111111] text-white placeholder-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-[#0a0a0a] ${validationErrors.purchasePrice ? "border-red-500" : "border-[#2a2a2a]"}`} placeholder="e.g., 150.00" />
              {validationErrors.purchasePrice && <p className="mt-1 text-sm text-red-600">{validationErrors.purchasePrice}</p>}
            </div>

            {/* Purchase Date */}
            <div>
              <label htmlFor="purchaseDate" className="block text-sm font-medium text-gray-300 mb-1">
                Purchase Date
              </label>
              <input id="purchaseDate" type="date" value={purchaseDate} onChange={(e) => setPurchaseDate(e.target.value)} disabled={isSubmitting} max={new Date().toISOString().split("T")[0]} className={`w-full px-3 py-2 border rounded-lg bg-[#111111] text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-[#0a0a0a] ${validationErrors.purchaseDate ? "border-red-500" : "border-[#2a2a2a]"}`} />
              {validationErrors.purchaseDate && <p className="mt-1 text-sm text-red-600">{validationErrors.purchaseDate}</p>}
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
                    {editPosition ? "Updating..." : "Adding..."}
                  </>
                ) : (
                  <>{editPosition ? "Update Position" : "Add Position"}</>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
