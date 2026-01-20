"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Loader2 } from "lucide-react";

interface StockChartProps {
  symbol: string;
  data?: ChartData[];
}

interface ChartData {
  date: string;
  price: number;
  volume: number;
}

export default function StockChart({ symbol, data: initialData }: StockChartProps) {
  const [chartData, setChartData] = useState<ChartData[]>(initialData || []);
  const [loading, setLoading] = useState(!initialData);
  const [timeframe, setTimeframe] = useState("1M");

  useEffect(() => {
    if (initialData) {
      setChartData(initialData);
      setLoading(false);
      return;
    }

    const fetchChartData = async () => {
      setLoading(true);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await axios.get(`${apiUrl}/api/stock/${symbol}/chart`, {
          params: { timeframe }
        });
        setChartData(response.data);
      } catch (err) {
        console.error("Failed to fetch chart data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, [symbol, timeframe, initialData]);

  const timeframes = ["1D", "1W", "1M", "3M", "1Y", "5Y"];

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold">Price Chart</h3>
        <div className="flex gap-2">
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-1 rounded-md text-sm transition-colors ${
                timeframe === tf
                  ? "bg-primary text-white"
                  : "bg-gray-800 hover:bg-gray-700 text-gray-300"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-80">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af' }}
            />
            <YAxis 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af' }}
              domain={['auto', 'auto']}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Area 
              type="monotone" 
              dataKey="price" 
              stroke="#3b82f6" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorPrice)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
