"use client";

import { AlertTriangle, X } from "lucide-react";
import { useState, useEffect } from "react";

interface RateLimitAlertProps {
  show: boolean;
  onClose: () => void;
}

export default function RateLimitAlert({ show, onClose }: RateLimitAlertProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      // Auto-hide after 10 seconds
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose();
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  if (!isVisible) return null;

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 max-w-2xl w-full mx-4 animate-slide-down">
      <div className="bg-yellow-900/95 border-2 border-yellow-600 rounded-lg shadow-2xl p-5">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <AlertTriangle className="w-8 h-8 text-yellow-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-yellow-200 font-bold text-lg mb-2">
            Free Tier Rate Limits Apply
            </h3>
            <div className="text-yellow-100 text-sm space-y-1.5">
              <p><strong>• US Stocks Only:</strong> AAPL, TSLA, GOOGL, MSFT, AMZN, NVDA, etc.</p>
              <p><strong>• Rate Limit:</strong> Search ONE stock per minute</p>
              <p><strong>• Not Supported:</strong> Futures (GC00), Options, Forex, Crypto</p>
              <p className="text-xs text-yellow-200/80 mt-2">
                💡 Wait 60 seconds between searches to avoid rate limit errors
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              setIsVisible(false);
              onClose();
            }}
            className="flex-shrink-0 text-yellow-300 hover:text-white transition-colors"
            aria-label="Close alert"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
