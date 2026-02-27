"use client";

import React, { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { PortfolioCompositionDataPoint } from "@/app/types/charts";

interface PortfolioCompositionChartProps {
  data: PortfolioCompositionDataPoint[];
  className?: string;
  height?: number;
}

// Default color palette for pie chart
const COLORS = [
  "#2563eb", // blue-600
  "#10b981", // green-500
  "#f59e0b", // amber-500
  "#ef4444", // red-500
  "#8b5cf6", // violet-500
  "#ec4899", // pink-500
  "#06b6d4", // cyan-500
  "#f97316", // orange-500
];

/**
 * Portfolio composition chart component
 * Displays allocation by stock as a pie chart with interactive legend
 * Validates: Requirements 6.2
 */
export const PortfolioCompositionChart: React.FC<PortfolioCompositionChartProps> = ({ data, className = "", height = 400 }) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  // Assign colors to data points
  const dataWithColors = data.map((item, index) => ({
    ...item,
    color: item.color || COLORS[index % COLORS.length],
  }));

  // Custom tooltip component
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="text-sm font-semibold text-gray-900">{dataPoint.ticker}</p>
          <p className="text-sm text-gray-700">Value: ${dataPoint.value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          <p className="text-sm text-gray-700">Percentage: {dataPoint.percentage.toFixed(2)}%</p>
        </div>
      );
    }
    return null;
  };

  // Custom label for pie slices
  const renderLabel = (entry: PortfolioCompositionDataPoint) => {
    return `${entry.ticker} (${entry.percentage.toFixed(1)}%)`;
  };

  const onPieEnter = (_: any, index: number) => {
    setActiveIndex(index);
  };

  const onPieLeave = () => {
    setActiveIndex(null);
  };

  return (
    <div className={className}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Composition</h3>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie data={dataWithColors} cx="50%" cy="50%" labelLine={false} label={renderLabel} outerRadius={120} fill="#8884d8" dataKey="value" onMouseEnter={onPieEnter} onMouseLeave={onPieLeave}>
            {dataWithColors.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} opacity={activeIndex === null || activeIndex === index ? 1 : 0.6} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry: any) => {
              const dataPoint = entry.payload;
              return `${dataPoint.ticker}: $${dataPoint.value.toLocaleString()}`;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
