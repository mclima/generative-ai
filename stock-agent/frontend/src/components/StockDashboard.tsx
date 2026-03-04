"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import StockChart from "./StockChart";
import StockMetrics from "./StockMetrics";
import AIInsights from "./AIInsights";
import NewsSection from "./NewsSection";
import StockTable from "./StockTable";
import { Loader2 } from "lucide-react";

interface StockDashboardProps {
  symbol: string;
}

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

interface ChartData {
  date: string;
  price: number;
  volume: number;
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

interface NewsArticle {
  title: string;
  description: string;
  url: string;
  published_at: string;
  source: string;
  sentiment?: "positive" | "negative" | "neutral";
}

interface Insight {
  type: "bullish" | "bearish" | "neutral";
  title: string;
  description: string;
}

interface AIInsightsData {
  insights: Insight[];
  summary: string;
}

export default function StockDashboard({ symbol }: StockDashboardProps) {
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
  const [newsData, setNewsData] = useState<NewsArticle[]>([]);
  const [insightsData, setInsightsData] = useState<any>(null);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [insightsRequested, setInsightsRequested] = useState(false);
  const [loading, setLoading] = useState(true);
  const [secondaryLoading, setSecondaryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Reset all data when symbol changes
    setStockData(null);
    setChartData([]);
    setHistoricalData([]);
    setNewsData([]);
    setInsightsData(null);
    setInsightsRequested(false);
    setInsightsLoading(false);
    setError(null);
    
    const fetchAllData = async () => {
      setLoading(true);
      
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        
        const priorityResults = await Promise.allSettled([
          axios.get(`${apiUrl}/api/stock/${symbol}`),
          axios.get(`${apiUrl}/api/stock/${symbol}/chart`, { params: { timeframe: "1M" } })
        ]);

        const [stockRes, chartRes] = priorityResults;

        if (stockRes.status === 'fulfilled') {
          setStockData(stockRes.value.data);
        } else {
          const errorMsg = stockRes.reason?.response?.data?.detail || stockRes.reason?.message || "Failed to fetch stock data";
          const statusCode = stockRes.reason?.response?.status;
          
          if (statusCode === 429) {
            setError("Rate limit exceeded. Please wait 60 seconds before searching again.");
          } else {
            setError(errorMsg);
          }
          console.error("Stock data error:", stockRes.reason);
        }

        if (chartRes.status === 'fulfilled') {
          console.log("Chart data received:", chartRes.value.data);
          setChartData(chartRes.value.data);
        } else {
          console.error("Chart data error:", chartRes.reason);
          console.error("Chart error details:", chartRes.reason?.response?.data);
        }

        setLoading(false);

        await new Promise(resolve => setTimeout(resolve, 500));

        setSecondaryLoading(true);

        const secondaryResults = await Promise.allSettled([
          axios.get(`${apiUrl}/api/stock/${symbol}/historical`),
          axios.get(`${apiUrl}/api/stock/${symbol}/news`)
        ]);

        const [historicalRes, newsRes] = secondaryResults;

        if (historicalRes.status === 'fulfilled') {
          setHistoricalData(historicalRes.value.data);
        } else {
          console.error("Historical data error:", historicalRes.reason);
        }

        if (newsRes.status === 'fulfilled') {
          setNewsData(newsRes.value.data);
        } else {
          console.error("News data error:", newsRes.reason);
        }

        setSecondaryLoading(false);
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || "Failed to fetch stock data. Please try again.";
        setError(errorMessage);
        console.error(err);
        setLoading(false);
      }
    };

    fetchAllData();
  }, [symbol]);

  const fetchInsights = async () => {
    if (insightsLoading || insightsData) return;
    
    setInsightsLoading(true);
    setInsightsRequested(true);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await axios.get(`${apiUrl}/api/stock/${symbol}/insights`);
      setInsightsData(response.data);
    } catch (err: any) {
      console.error("Insights error:", err);
    } finally {
      setInsightsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-3 text-lg">Loading stock data...</span>
      </div>
    );
  }

  if (error && !stockData) {
    return (
      <div className="card bg-red-900/20 border-2 border-red-700">
        <div className="flex items-start gap-3">
          <div className="text-red-400 text-2xl">⚠️</div>
          <div className="flex-1">
            <h3 className="text-red-300 font-bold text-lg mb-2">Error Loading Stock Data</h3>
            <p className="text-red-200 mb-3">{error}</p>
            {error.includes("No data found") && (
              <div className="bg-red-950/50 border border-red-800 rounded p-3 text-sm text-red-100">
                <p className="font-semibold mb-1">💡 Tip:</p>
                <p>Only US stocks are supported like AAPL, TSLA, GOOGL, MSFT, AMZN, NVDA, etc.</p>
                <p className="mt-1">Futures, options, forex, and crypto are not available.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!stockData) {
    return null;
  }

  return (
    <div className="space-y-6">
      <StockMetrics data={stockData} />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <StockChart symbol={symbol} data={chartData} />
        </div>
        <div>
          <AIInsights 
            symbol={symbol} 
            data={insightsData} 
            isLoading={insightsLoading}
            onFetchInsights={fetchInsights}
            insightsRequested={insightsRequested}
          />
        </div>
      </div>

      <StockTable symbol={symbol} data={historicalData} isLoading={secondaryLoading && !historicalData.length} />
      
      <NewsSection symbol={symbol} data={newsData} isLoading={secondaryLoading && newsData.length === 0} />
    </div>
  );
}
