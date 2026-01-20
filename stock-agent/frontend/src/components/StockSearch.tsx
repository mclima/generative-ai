"use client";

import { useState } from "react";
import { Search } from "lucide-react";

interface StockSearchProps {
  onSymbolSelect: (symbol: string) => void;
}

export default function StockSearch({ onSymbolSelect }: StockSearchProps) {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSymbolSelect(inputValue.trim().toUpperCase());
    }
  };

  const popularStocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"];

  return (
    <div className="card">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter US stock symbol (e.g., AAPL, TSLA)"
            className="w-full pl-12 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            aria-label="Stock symbol search"
          />
        </div>
        <button type="submit" className="btn-primary">
          Analyze
        </button>
      </form>

      <div className="mt-4">
        <p className="text-sm text-gray-400 mb-2">Popular stocks:</p>
        <div className="flex flex-wrap gap-2">
          {popularStocks.map((symbol) => (
            <button
              key={symbol}
              onClick={() => onSymbolSelect(symbol)}
              className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded-md text-sm transition-colors"
            >
              {symbol}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
