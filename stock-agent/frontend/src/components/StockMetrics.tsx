"use client";

import { TrendingUp, TrendingDown, DollarSign, Activity } from "lucide-react";

interface StockData {
  symbol: string;
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  high_52week: number;
  low_52week: number;
}

interface StockMetricsProps {
  data: StockData;
}

export default function StockMetrics({ data }: StockMetricsProps) {
  const isPositive = data.change >= 0;
  const formatNumber = (num: number) => {
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toFixed(2)}`;
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold">{data.symbol}</h2>
          <p className="text-gray-400">Real-time data</p>
        </div>
        <div className="text-right">
          <div className="text-4xl font-bold">${data.current_price.toFixed(2)}</div>
          <div className={`flex items-center justify-end mt-1 ${isPositive ? "text-success" : "text-danger"}`}>
            {isPositive ? <TrendingUp className="w-5 h-5 mr-1" /> : <TrendingDown className="w-5 h-5 mr-1" />}
            <span className="font-semibold">
              {isPositive ? "+" : ""}{data.change.toFixed(2)} ({isPositive ? "+" : ""}{data.change_percent.toFixed(2)}%)
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center text-gray-400 mb-2">
            <Activity className="w-4 h-4 mr-2" />
            <span className="text-sm">Volume</span>
          </div>
          <div className="text-xl font-semibold">{(data.volume / 1e6).toFixed(2)}M</div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="flex items-center text-gray-400 mb-2">
            <DollarSign className="w-4 h-4 mr-2" />
            <span className="text-sm">Market Cap</span>
          </div>
          <div className="text-xl font-semibold">{formatNumber(data.market_cap)}</div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">P/E Ratio</div>
          <div className="text-xl font-semibold">{data.pe_ratio.toFixed(2)}</div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">52W Range</div>
          <div className="text-sm font-semibold">
            ${data.low_52week.toFixed(2)} - ${data.high_52week.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
}
