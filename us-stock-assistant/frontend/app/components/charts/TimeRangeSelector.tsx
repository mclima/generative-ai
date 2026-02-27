"use client";

import React from "react";
import { TimeRange } from "@/app/types/charts";

interface TimeRangeSelectorProps {
  selectedRange: TimeRange;
  onRangeChange: (range: TimeRange) => void;
  className?: string;
}

const TIME_RANGES: TimeRange[] = ["1D", "1W", "1M", "3M", "1Y", "ALL"];

/**
 * Time range selector component for charts
 * Provides buttons to switch between different time periods
 */
export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({ selectedRange, onRangeChange, className = "" }) => {
  return (
    <div className={`flex gap-2 ${className}`}>
      {TIME_RANGES.map((range) => (
        <button key={range} onClick={() => onRangeChange(range)} className={`px-3 py-1 rounded text-sm font-medium transition-colors ${selectedRange === range ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`} aria-label={`Select ${range} time range`} aria-pressed={selectedRange === range}>
          {range}
        </button>
      ))}
    </div>
  );
};
