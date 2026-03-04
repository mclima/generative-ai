"use client";

import { Info, AlertCircle } from "lucide-react";
import { useState } from "react";

export default function InfoBanner() {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="mb-6 bg-blue-900/30 border border-blue-700/50 rounded-lg p-4 relative">
      <button
        onClick={() => setIsVisible(false)}
        className="absolute top-3 right-3 text-gray-400 hover:text-white transition-colors"
        aria-label="Close banner"
      >
        ✕
      </button>
      
      <div className="flex gap-3">
        <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-blue-300 font-semibold mb-2 flex items-center gap-2">
            Supported Markets
          </h3>
          <div className="text-sm text-gray-300 space-y-1.5">
            <p><strong>• US Stocks:</strong> AAPL, TSLA, GOOGL, MSFT, AMZN, NVDA</p>
            <p><strong>• Crypto:</strong> BTC, ETH, and other cryptocurrencies</p>
            <p className="text-xs text-gray-400 mt-1">Futures, options, and forex are not available</p>
          </div>
        </div>
      </div>
    </div>
  );
}
