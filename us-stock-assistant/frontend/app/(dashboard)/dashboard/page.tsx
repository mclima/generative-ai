"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { portfolioApi } from "@/app/lib/api/portfolio";
import { stocksApi } from "@/app/lib/api/stocks";
import { useAuth } from "@/app/contexts/AuthContext";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [totalValue, setTotalValue] = useState(0);
  const [totalGainLoss, setTotalGainLoss] = useState(0);
  const [totalGainLossPercent, setTotalGainLossPercent] = useState(0);
  const [positionCount, setPositionCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    const load = async () => {
      try {
        const portfolio = await portfolioApi.getPortfolio();
        const positions = portfolio.positions || [];
        setPositionCount(positions.length);

        if (positions.length > 0) {
          const tickers = positions.map((p) => p.ticker);
          const prices = await stocksApi.getBatchPrices(tickers);
          let value = 0, cost = 0;
          positions.forEach((pos) => {
            const currentPrice = prices[pos.ticker]?.price || pos.purchase_price;
            value += currentPrice * pos.quantity;
            cost += pos.purchase_price * pos.quantity;
          });
          setTotalValue(value);
          setTotalGainLoss(value - cost);
          setTotalGainLossPercent(cost > 0 ? ((value - cost) / cost) * 100 : 0);
        }
      } catch {
        // silently fail
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user, authLoading]);

  const fmt = (n: number) => n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <div className="space-y-6 text-white">
      <h1 className="text-2xl sm:text-3xl font-bold text-white">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 sm:p-6 rounded-lg shadow hover:shadow-md transition-shadow">
          <h2 className="text-lg sm:text-xl font-semibold mb-2 text-gray-300">Portfolio Value</h2>
          <p className="text-2xl sm:text-3xl font-bold text-blue-600">{loading ? "..." : `$${fmt(totalValue)}`}</p>
          <p className="text-xs sm:text-sm text-gray-500 mt-1">Total value of all positions</p>
        </div>
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 sm:p-6 rounded-lg shadow hover:shadow-md transition-shadow">
          <h2 className="text-lg sm:text-xl font-semibold mb-2 text-gray-300">Total Gain/Loss</h2>
          <p className={`text-2xl sm:text-3xl font-bold ${totalGainLoss >= 0 ? "text-green-500" : "text-red-500"}`}>
            {loading ? "..." : `${totalGainLoss >= 0 ? "+" : ""}$${fmt(totalGainLoss)}`}
          </p>
          <p className={`text-xs sm:text-sm mt-1 ${totalGainLoss >= 0 ? "text-green-500" : "text-red-500"}`}>
            {loading ? "" : `${totalGainLossPercent >= 0 ? "+" : ""}${totalGainLossPercent.toFixed(2)}%`}
          </p>
          <p className="text-xs sm:text-sm text-gray-500 mt-1">Unrealized gains/losses</p>
        </div>
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 sm:p-6 rounded-lg shadow hover:shadow-md transition-shadow sm:col-span-2 xl:col-span-1">
          <h2 className="text-lg sm:text-xl font-semibold mb-2 text-gray-300">Active Positions</h2>
          <p className="text-2xl sm:text-3xl font-bold text-white">{loading ? "..." : positionCount}</p>
          <p className="text-xs sm:text-sm text-gray-500 mt-1">Number of stocks held</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 sm:p-6 rounded-lg shadow">
          <h2 className="text-lg sm:text-xl font-semibold mb-4 text-white">Recent Activity</h2>
          <p className="text-sm text-gray-500">No recent activity</p>
        </div>
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 sm:p-6 rounded-lg shadow">
          <h2 className="text-lg sm:text-xl font-semibold mb-4 text-white">Quick Actions</h2>
          <div className="space-y-2">
            <button onClick={() => router.push("/portfolio")} className="w-full text-left px-4 py-2 bg-blue-900 hover:bg-blue-800 rounded text-sm sm:text-base text-blue-300 transition-colors">Add Stock Position</button>
            <button onClick={() => router.push("/alerts")} className="w-full text-left px-4 py-2 bg-blue-900 hover:bg-blue-800 rounded text-sm sm:text-base text-blue-300 transition-colors">Create Price Alert</button>
            <button onClick={() => router.push("/market")} className="w-full text-left px-4 py-2 bg-blue-900 hover:bg-blue-800 rounded text-sm sm:text-base text-blue-300 transition-colors">View Market Overview</button>
          </div>
        </div>
      </div>
    </div>
  );
}
