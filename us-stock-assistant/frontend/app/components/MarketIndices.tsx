"use client";

import type { MarketIndex } from "@/app/types/market";

interface MarketIndicesProps {
  indices: MarketIndex[];
}

export default function MarketIndices({ indices }: MarketIndicesProps) {
  const getChangeColor = (change: number) => {
    if (change > 0) return "text-green-400";
    if (change < 0) return "text-red-400";
    return "text-gray-400";
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) {
      return (
        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
        </svg>
      );
    }
    if (change < 0) {
      return (
        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-white mb-4">Major Market Indices</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {indices.map((index) => (
          <div key={index.symbol} className="border border-[#2a2a2a] bg-[#111111] rounded-lg p-4 hover:border-blue-700 transition-shadow">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-white">{index.name}</h3>
              <span className="text-xs text-gray-500">{index.symbol}</span>
            </div>
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-2xl font-bold text-white">
                {index.value.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>
            <div className={`flex items-center gap-1 ${getChangeColor(index.change)}`}>
              {getChangeIcon(index.change)}
              <span className="font-medium">
                {index.change > 0 ? "+" : ""}
                {index.change.toFixed(2)}
              </span>
              <span className="font-medium">
                ({index.change_percent > 0 ? "+" : ""}
                {index.change_percent.toFixed(2)}%)
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
