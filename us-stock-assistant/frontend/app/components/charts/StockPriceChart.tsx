"use client";

import React, { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Brush, ReferenceLine } from "recharts";
import { ChartWrapper } from "./ChartWrapper";
import { TimeRangeSelector } from "./TimeRangeSelector";
import { TimeRange, StockPriceDataPoint, LineChartDataPoint } from "@/app/types/charts";
import { usePreferences } from "@/app/contexts/PreferencesContext";

interface StockPriceChartProps {
  data: StockPriceDataPoint[] | LineChartDataPoint[];
  ticker: string;
  chartType?: "line" | "candlestick";
  className?: string;
  height?: number;
}

/**
 * Stock price history chart component
 * Displays price history as line chart with time range selector and zoom/pan
 * Validates: Requirements 6.3, 6.5
 */
export const StockPriceChart: React.FC<StockPriceChartProps> = ({ data, ticker, chartType, className = "", height = 400 }) => {
  const { preferences } = usePreferences();
  const [selectedRange, setSelectedRange] = useState<TimeRange>(preferences?.default_time_range || "1M");

  // Use preferences for default chart type if not explicitly provided
  const effectiveChartType = chartType || preferences?.default_chart_type || "line";

  // Filter data based on selected time range
  const filterDataByRange = (range: TimeRange): typeof data => {
    if (range === "ALL" || data.length === 0) {
      return data;
    }

    const now = Date.now();
    const rangeInMs: Record<Exclude<TimeRange, "ALL">, number> = {
      "1D": 24 * 60 * 60 * 1000,
      "1W": 7 * 24 * 60 * 60 * 1000,
      "1M": 30 * 24 * 60 * 60 * 1000,
      "3M": 90 * 24 * 60 * 60 * 1000,
      "1Y": 365 * 24 * 60 * 60 * 1000,
    };

    const cutoffTime = now - rangeInMs[range];
    return data.filter((point) => point.timestamp >= cutoffTime);
  };

  const filteredData = filterDataByRange(selectedRange);

  // Custom tooltip component
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;

      if ("close" in dataPoint) {
        // Candlestick data
        return (
          <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
            <p className="text-sm font-medium text-gray-900">{dataPoint.date}</p>
            <p className="text-sm text-gray-700">Open: ${dataPoint.open.toFixed(2)}</p>
            <p className="text-sm text-gray-700">High: ${dataPoint.high.toFixed(2)}</p>
            <p className="text-sm text-gray-700">Low: ${dataPoint.low.toFixed(2)}</p>
            <p className="text-sm text-gray-700">Close: ${dataPoint.close.toFixed(2)}</p>
            <p className="text-sm text-gray-700">Volume: {dataPoint.volume.toLocaleString()}</p>
          </div>
        );
      } else {
        // Line chart data
        return (
          <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
            <p className="text-sm font-medium text-gray-900">{dataPoint.date}</p>
            <p className="text-sm text-gray-700">Price: ${dataPoint.value.toFixed(2)}</p>
          </div>
        );
      }
    }
    return null;
  };

  // Determine which data key to use based on chart type
  const priceDataKey = effectiveChartType === "candlestick" && "close" in filteredData[0] ? "close" : "value";

  return (
    <div className={className}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{ticker} Price History</h3>
        <TimeRangeSelector selectedRange={selectedRange} onRangeChange={setSelectedRange} />
      </div>
      <ChartWrapper height={height}>
        <LineChart data={filteredData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: "12px" }} />
          <YAxis stroke="#6b7280" style={{ fontSize: "12px" }} tickFormatter={(value) => `$${value.toFixed(2)}`} domain={["auto", "auto"]} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line type="monotone" dataKey={priceDataKey} stroke="#2563eb" strokeWidth={2} dot={false} name="Price" activeDot={{ r: 6 }} />
          {/* Brush component provides zoom and pan functionality */}
          <Brush dataKey="date" height={30} stroke="#2563eb" fill="#eff6ff" />
        </LineChart>
      </ChartWrapper>
    </div>
  );
};
