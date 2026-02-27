"use client";

import { useState, useEffect, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { ResponsiveContainer, AreaChart, Area, ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import { stocksApi } from "@/app/lib/api/stocks";
import { portfolioApi } from "@/app/lib/api/portfolio";
import { useAuth } from "@/app/contexts/AuthContext";
import { usePreferences } from "@/app/contexts/PreferencesContext";
import type { StockPrice, CompanyInfo, FinancialMetrics, HistoricalData } from "@/app/types/stocks";
import type { StockPositionInput } from "@/app/types/portfolio";
import AddStockModal from "@/app/components/AddStockModal";
import StockNewsSection from "@/app/components/StockNewsSection";
import StockAnalysisPanel from "@/app/components/StockAnalysisPanel";

const TIME_RANGES = [
  { label: "1W", days: 7 },
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "6M", days: 180 },
  { label: "1Y", days: 365 },
];

export default function StockDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const ticker = params.ticker as string;

  const [stockPrice, setStockPrice] = useState<StockPrice | null>(null);
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [financialMetrics, setFinancialMetrics] = useState<FinancialMetrics | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [isAddingToPortfolio, setIsAddingToPortfolio] = useState(false);
  const { preferences } = usePreferences();
  const [selectedRange, setSelectedRange] = useState("1Y");
  const [chartType, setChartType] = useState<"line" | "candlestick">("line");
  const [addSuccess, setAddSuccess] = useState(false);

  useEffect(() => {
    if (preferences) {
      const prefRange = preferences.default_time_range;
      const mapped = prefRange === "ALL" ? "1Y" : prefRange;
      setSelectedRange(mapped);
      setChartType(preferences.default_chart_type === "candlestick" ? "candlestick" : "line");
    }
  }, [preferences]);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    if (ticker) loadStockData();
  }, [ticker, user, authLoading]);

  const loadStockData = async (retryCount = 0) => {
    setIsLoading(true);
    setError(null);
    try {
      const [detailsResult, historicalDataResult] = await Promise.allSettled([
        stocksApi.getStockDetails(ticker.toUpperCase()),
        stocksApi.getHistoricalData(
          ticker.toUpperCase(),
          new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
          new Date().toISOString().split("T")[0],
        ),
      ]);
      if (detailsResult.status === "fulfilled") {
        setStockPrice(detailsResult.value.price);
        setCompanyInfo(detailsResult.value.company);
        setFinancialMetrics(detailsResult.value.metrics);
      } else {
        if (retryCount < 1) {
          await new Promise((r) => setTimeout(r, 1500));
          return loadStockData(retryCount + 1);
        }
        setError("Failed to load stock data.");
      }
      if (historicalDataResult.status === "fulfilled") {
        setHistoricalData(historicalDataResult.value);
      }
    } catch {
      if (retryCount < 1) {
        await new Promise((r) => setTimeout(r, 1500));
        return loadStockData(retryCount + 1);
      }
      setError("An unexpected error occurred.");
    } finally {
      if (retryCount === 0 || retryCount >= 1) setIsLoading(false);
    }
  };

  const filteredData = useMemo(() => {
    const range = TIME_RANGES.find((r) => r.label === selectedRange);
    if (!range || !historicalData.length) return historicalData;
    const cutoff = new Date(Date.now() - range.days * 24 * 60 * 60 * 1000);
    return historicalData.filter((d) => new Date(d.date) >= cutoff);
  }, [historicalData, selectedRange]);

  const chartColor = useMemo(() => {
    if (filteredData.length < 2) return "#3b82f6";
    return filteredData[filteredData.length - 1].close >= filteredData[0].close ? "#22c55e" : "#ef4444";
  }, [filteredData]);

  const handleAddToPortfolio = async (position: StockPositionInput) => {
    setIsAddingToPortfolio(true);
    try {
      await portfolioApi.addPosition(position);
      setShowAddModal(false);
      setAddSuccess(true);
      setTimeout(() => setAddSuccess(false), 3000);
    } catch {
      // error handled in modal
    } finally {
      setIsAddingToPortfolio(false);
    }
  };

  const fmt = (v: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(v);
  const fmtNum = (v: number) => new Intl.NumberFormat("en-US").format(v);
  const fmtCap = (v: number) => {
    if (v >= 1e12) return `$${(v / 1e12).toFixed(2)}T`;
    if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
    if (v >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
    return fmt(v);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading {ticker?.toUpperCase()}...</p>
        </div>
      </div>
    );
  }

  if (error && !stockPrice) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <p className="text-red-400 text-xl">{error}</p>
        <button onClick={() => router.back()} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Go Back</button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back button */}
      <button onClick={() => router.back()} className="flex items-center text-gray-400 hover:text-white mb-6 transition-colors">
        <svg className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </button>

      {/* Success banner */}
      {addSuccess && (
        <div className="mb-4 p-4 bg-green-900/20 border border-green-800 rounded-lg text-green-400 flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
          {ticker?.toUpperCase()} added to portfolio!
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-1">{companyInfo?.name || ticker?.toUpperCase()}</h1>
          <div className="flex items-center gap-3">
            <span className="text-lg font-semibold text-gray-400">{ticker?.toUpperCase()}</span>
            {companyInfo?.sector && <span className="text-xs px-2 py-1 bg-[#2a2a2a] text-gray-400 rounded">{companyInfo.sector}</span>}
          </div>
        </div>
        <button onClick={() => setShowAddModal(true)} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors">
          + Add to Portfolio
        </button>
      </div>

      {/* Price card */}
      {stockPrice && (
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6 mb-6">
          <div className="flex items-end gap-4 flex-wrap">
            <span className="text-5xl font-bold text-white">{fmt(stockPrice.price)}</span>
            <div className={`flex items-center text-xl font-semibold ${stockPrice.change >= 0 ? "text-green-400" : "text-red-400"}`}>
              {stockPrice.change >= 0 ? "▲" : "▼"} {stockPrice.change >= 0 ? "+" : ""}{fmt(stockPrice.change)} ({stockPrice.change >= 0 ? "+" : ""}{stockPrice.change_percent.toFixed(2)}%)
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">Volume: {fmtNum(stockPrice.volume)} · Last updated: {new Date(stockPrice.timestamp).toLocaleString()}</p>
        </div>
      )}

      {/* Price Chart */}
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h2 className="text-xl font-bold text-white">Price Chart</h2>
          <div className="flex items-center gap-3">
            {/* Chart type toggle */}
            <div className="flex gap-1 bg-[#111111] rounded-md p-1">
              <button onClick={() => setChartType("line")} className={`px-3 py-1 text-xs rounded font-medium transition-colors ${chartType === "line" ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"}`}>Line</button>
              <button onClick={() => setChartType("candlestick")} className={`px-3 py-1 text-xs rounded font-medium transition-colors ${chartType === "candlestick" ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"}`}>Candlestick</button>
            </div>
            {/* Time range selector */}
            <div className="flex gap-1">
              {TIME_RANGES.map((r) => (
                <button
                  key={r.label}
                  onClick={() => setSelectedRange(r.label)}
                  className={`px-3 py-1 text-sm rounded font-medium transition-colors ${selectedRange === r.label ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white hover:bg-[#2a2a2a]"}`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>
        </div>
        {filteredData.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            {chartType === "candlestick" ? (
              <ComposedChart data={filteredData} margin={{ top: 5, right: 5, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric" })} interval="preserveStartEnd" stroke="#2a2a2a" />
                <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => `$${v.toFixed(0)}`} domain={["auto", "auto"]} stroke="#2a2a2a" width={60} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: "8px", color: "#fff" }}
                  labelStyle={{ color: "#9ca3af" }}
                  formatter={(value: number, name: string) => [`$${value.toFixed(2)}`, name]}
                  labelFormatter={(label) => new Date(label).toLocaleDateString("en-US", { weekday: "short", year: "numeric", month: "short", day: "numeric" })}
                />
                <Bar dataKey="close" fill={chartColor} opacity={0.8} name="Close" />
                <Bar dataKey="open" fill="#6b7280" opacity={0.5} name="Open" />
              </ComposedChart>
            ) : (
              <AreaChart data={filteredData} margin={{ top: 5, right: 5, left: 10, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={chartColor} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
                <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric" })} interval="preserveStartEnd" stroke="#2a2a2a" />
                <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => `$${v.toFixed(0)}`} domain={["auto", "auto"]} stroke="#2a2a2a" width={60} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1a1a1a", border: "1px solid #2a2a2a", borderRadius: "8px", color: "#fff" }}
                  labelStyle={{ color: "#9ca3af" }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, "Close"]}
                  labelFormatter={(label) => new Date(label).toLocaleDateString("en-US", { weekday: "short", year: "numeric", month: "short", day: "numeric" })}
                />
                <Area type="monotone" dataKey="close" stroke={chartColor} strokeWidth={2} fill="url(#colorClose)" dot={false} activeDot={{ r: 4, fill: chartColor }} />
              </AreaChart>
            )}
          </ResponsiveContainer>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500">No historical data available</div>
        )}
      </div>

      {/* Company Info + Financial Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {companyInfo && (
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">Company Information</h2>
            <div className="space-y-3">
              <div><p className="text-xs text-gray-500 uppercase tracking-wider">Sector</p><p className="text-white font-medium">{companyInfo.sector || "N/A"}</p></div>
              <div><p className="text-xs text-gray-500 uppercase tracking-wider">Industry</p><p className="text-white font-medium">{companyInfo.industry || "N/A"}</p></div>
              <div><p className="text-xs text-gray-500 uppercase tracking-wider">Market Cap</p><p className="text-white font-medium">{fmtCap(companyInfo.market_cap)}</p></div>
              {companyInfo.description && (
                <div><p className="text-xs text-gray-500 uppercase tracking-wider mb-1">About</p><p className="text-gray-400 text-sm leading-relaxed line-clamp-4">{companyInfo.description}</p></div>
              )}
            </div>
          </div>
        )}

        {financialMetrics && (
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">Financial Metrics</h2>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: "P/E Ratio", value: financialMetrics.pe_ratio != null ? financialMetrics.pe_ratio.toFixed(2) : "N/A" },
                { label: "EPS", value: financialMetrics.eps != null ? fmt(financialMetrics.eps) : "N/A" },
                { label: "Dividend Yield", value: financialMetrics.dividend_yield != null ? `${financialMetrics.dividend_yield.toFixed(2)}%` : "N/A" },
                { label: "Beta", value: financialMetrics.beta != null ? financialMetrics.beta.toFixed(2) : "N/A" },
                { label: "52W High", value: financialMetrics.fifty_two_week_high != null ? fmt(financialMetrics.fifty_two_week_high) : "N/A" },
                { label: "52W Low", value: financialMetrics.fifty_two_week_low != null ? fmt(financialMetrics.fifty_two_week_low) : "N/A" },
              ].map(({ label, value }) => (
                <div key={label} className="bg-[#111111] rounded-lg p-3">
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
                  <p className="text-white font-semibold text-lg">{value}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* AI Analysis */}
      <div className="mb-6">
        <StockAnalysisPanel ticker={ticker?.toUpperCase()} />
      </div>

      {/* News */}
      <StockNewsSection ticker={ticker?.toUpperCase()} limit={5} />

      {/* Add to Portfolio Modal */}
      <AddStockModal isOpen={showAddModal} onClose={() => setShowAddModal(false)} onSubmit={handleAddToPortfolio} isSubmitting={isAddingToPortfolio} initialTicker={ticker?.toUpperCase()} />
    </div>
  );
}
