"use client";

import React, { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import { ChartWrapper } from "./ChartWrapper";
import { TimeRangeSelector } from "./TimeRangeSelector";
import { TimeRange, PortfolioValueDataPoint } from "@/app/types/charts";

interface PortfolioValueChartProps {
  data: PortfolioValueDataPoint[];
  className?: string;
  height?: number;
}

/**
 * Portfolio value chart component
 * Displays portfolio value over time as a line chart with time range selector
 * Validates: Requirements 6.1, 6.5
 */
export const PortfolioValueChart: React.FC<PortfolioValueChartProps> = ({ data, className = "", height = 400 }) => {
  const [selectedRange, setSelectedRange] = useState<TimeRange>("1M");

  // Filter data based on selected time range
  const filterDataByRange = (range: TimeRange): PortfolioValueDataPoint[] => {
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
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="text-sm font-medium text-gray-900">{dataPoint.date}</p>
          <p className="text-sm text-gray-700">Value: ${dataPoint.value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={className}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Portfolio Value Over Time</h3>
        <TimeRangeSelector selectedRange={selectedRange} onRangeChange={setSelectedRange} />
      </div>
      <ChartWrapper height={height}>
        <LineChart data={filteredData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: "12px" }} />
          <YAxis stroke="#6b7280" style={{ fontSize: "12px" }} tickFormatter={(value) => `$${value.toLocaleString()}`} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} dot={false} name="Portfolio Value" activeDot={{ r: 6 }} />
        </LineChart>
      </ChartWrapper>
    </div>
  );
};
