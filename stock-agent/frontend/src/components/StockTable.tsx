"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Table, Loader2 } from "lucide-react";

interface StockTableProps {
  symbol: string;
  data?: HistoricalData[];
  isLoading?: boolean;
}

interface HistoricalData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change_percent: number;
}

export default function StockTable({ symbol, data: initialData, isLoading: externalLoading }: StockTableProps) {
  const [data, setData] = useState<HistoricalData[]>(initialData || []);
  const [loading, setLoading] = useState(!initialData);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setData(initialData);
      setLoading(false);
      return;
    }

    const fetchTableData = async () => {
      setLoading(true);
      setError(null);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await axios.get(`${apiUrl}/api/stock/${symbol}/historical`);
        setData(response.data);
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || "Failed to load historical data. Please try again.";
        setError(errorMessage);
        console.error("Failed to fetch historical data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTableData();
  }, [symbol, initialData]);

  const isLoading = externalLoading !== undefined ? externalLoading : loading;

  return (
    <div className="card">
      <div className="flex items-center mb-6">
        <Table className="w-6 h-6 text-green-500 mr-2" />
        <h3 className="text-xl font-semibold">Historical Data</h3>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : error ? (
        <div className="bg-red-900/20 border border-red-800 rounded p-4">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      ) : data.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <p>No historical data available for this stock.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Date</th>
                <th className="text-right py-3 px-4 text-gray-400 font-semibold">Open</th>
                <th className="text-right py-3 px-4 text-gray-400 font-semibold">High</th>
                <th className="text-right py-3 px-4 text-gray-400 font-semibold">Low</th>
                <th className="text-right py-3 px-4 text-gray-400 font-semibold">Close</th>
                <th className="text-right py-3 px-4 text-gray-400 font-semibold">Volume</th>
                <th className="text-right py-3 px-4 text-gray-400 font-semibold">Change %</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr
                  key={index}
                  className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors"
                >
                  <td className="py-3 px-4">{row.date}</td>
                  <td className="py-3 px-4 text-right">${row.open.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right">${row.high.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right">${row.low.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right font-semibold">${row.close.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right">{(row.volume / 1e6).toFixed(2)}M</td>
                  <td className={`py-3 px-4 text-right font-semibold ${
                    row.change_percent >= 0 ? "text-success" : "text-danger"
                  }`}>
                    {row.change_percent >= 0 ? "+" : ""}{row.change_percent.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
