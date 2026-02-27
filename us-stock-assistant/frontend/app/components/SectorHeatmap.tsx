"use client";

import { useState } from "react";
import type { SectorPerformance } from "@/app/types/market";

interface SectorHeatmapProps {
  sectors: SectorPerformance[];
}

export default function SectorHeatmap({ sectors }: SectorHeatmapProps) {
  const [hoveredSector, setHoveredSector] = useState<string | null>(null);

  const getPerformanceColor = (changePercent: number) => {
    if (changePercent >= 3) return "bg-green-600 text-white";
    if (changePercent >= 1.5) return "bg-green-500 text-white";
    if (changePercent >= 0.5) return "bg-green-400 text-white";
    if (changePercent > 0) return "bg-green-300 text-gray-900";
    if (changePercent === 0) return "bg-gray-300 text-gray-900";
    if (changePercent > -0.5) return "bg-red-300 text-gray-900";
    if (changePercent > -1.5) return "bg-red-400 text-white";
    if (changePercent > -3) return "bg-red-500 text-white";
    return "bg-red-600 text-white";
  };

  const getPerformanceLabel = (changePercent: number) => {
    if (changePercent >= 2) return "Strong Gain";
    if (changePercent >= 1) return "Moderate Gain";
    if (changePercent > 0) return "Slight Gain";
    if (changePercent === 0) return "Unchanged";
    if (changePercent > -1) return "Slight Loss";
    if (changePercent > -2) return "Moderate Loss";
    return "Strong Loss";
  };

  const sortedSectors = [...sectors].sort((a, b) => b.change_percent - a.change_percent);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Sector Performance Heatmap</h2>
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 bg-green-600 rounded"></span>
            Strong Gain
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 bg-gray-300 rounded"></span>
            Neutral
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 bg-red-600 rounded"></span>
            Strong Loss
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {sortedSectors.map((sector) => (
          <div key={sector.sector} className={`relative rounded-lg p-4 cursor-pointer transition-all hover:scale-105 hover:shadow-lg ${getPerformanceColor(sector.change_percent)}`} onMouseEnter={() => setHoveredSector(sector.sector)} onMouseLeave={() => setHoveredSector(null)}>
            <div className="text-center">
              <p className="font-semibold text-sm mb-1">{sector.sector}</p>
              <p className="text-2xl font-bold">
                {sector.change_percent > 0 ? "+" : ""}
                {sector.change_percent.toFixed(2)}%
              </p>
              <p className="text-xs opacity-90 mt-1">{getPerformanceLabel(sector.change_percent)}</p>
            </div>

            {/* Tooltip */}
            {hoveredSector === sector.sector && (
              <div className="absolute z-10 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 bg-gray-900 text-white text-xs rounded-lg p-3 shadow-xl">
                <div className="mb-2">
                  <p className="font-semibold mb-1">{sector.sector}</p>
                  <p className="text-gray-300">
                    Change: {sector.change_percent > 0 ? "+" : ""}
                    {sector.change_percent.toFixed(2)}%
                  </p>
                </div>
                {sector.top_performers.length > 0 && (
                  <div className="mb-2">
                    <p className="font-semibold text-green-400 mb-1">Top Performers:</p>
                    <p className="text-gray-300">{sector.top_performers.join(", ")}</p>
                  </div>
                )}
                {sector.bottom_performers.length > 0 && (
                  <div>
                    <p className="font-semibold text-red-400 mb-1">Bottom Performers:</p>
                    <p className="text-gray-300">{sector.bottom_performers.join(", ")}</p>
                  </div>
                )}
                {/* Arrow pointing down */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                  <div className="border-4 border-transparent border-t-gray-900"></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {sectors.length === 0 && <p className="text-center text-gray-500 py-4">No sector data available</p>}
    </div>
  );
}
