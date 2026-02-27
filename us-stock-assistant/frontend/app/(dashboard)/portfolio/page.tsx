"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/contexts/AuthContext";
import { useNotifications } from "@/app/contexts/NotificationContext";
import { portfolioApi } from "@/app/lib/api/portfolio";
import { useDataRefresh } from "@/app/hooks/useDataRefresh";
import AddStockModal from "@/app/components/AddStockModal";
import ConfirmDialog from "@/app/components/ConfirmDialog";
import PortfolioMetrics from "@/app/components/PortfolioMetrics";
import PortfolioAnalysisPanel from "@/app/components/PortfolioAnalysisPanel";
import ImportPortfolioModal from "@/app/components/ImportPortfolioModal";
import type { Portfolio, PortfolioMetrics as PortfolioMetricsType, StockPosition } from "@/app/types/portfolio";
import type { StockPrice } from "@/app/types/stocks";
import { handleApiError } from "@/app/lib/api-client";

export default function PortfolioPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [metrics, setMetrics] = useState<PortfolioMetricsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingPosition, setEditingPosition] = useState<StockPosition | null>(null);
  const [deletingPosition, setDeletingPosition] = useState<StockPosition | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importSuccess, setImportSuccess] = useState(false);
  const [importedCount, setImportedCount] = useState(0);

  // Close export menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showExportMenu && !target.closest(".export-menu-container")) {
        setShowExportMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showExportMenu]);

  // Use global WebSocket for real-time price updates
  const { isConnected, subscribe, unsubscribe, onPriceUpdate } = useNotifications();

  // Register price update handler
  useEffect(() => {
    onPriceUpdate((priceData) => {
      // Update portfolio positions with new prices
      setPortfolio((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          positions: prev.positions.map((pos) =>
            pos.ticker === priceData.ticker
              ? {
                  ...pos,
                  current_price: priceData.price,
                  current_value: priceData.price * pos.quantity,
                  gain_loss: (priceData.price - pos.purchase_price) * pos.quantity,
                  gain_loss_percent: ((priceData.price - pos.purchase_price) / pos.purchase_price) * 100,
                }
              : pos,
          ),
        };
      });
    });
  }, [onPriceUpdate]);

  // Subscribe to tickers when portfolio loads and WebSocket is connected
  useEffect(() => {
    if (isConnected && portfolio?.positions && portfolio.positions.length > 0) {
      const tickers = portfolio.positions.map((pos) => pos.ticker);
      subscribe(tickers);
    }
  }, [isConnected, portfolio, subscribe]);

  const loadPortfolio = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [portfolioData, metricsData] = await Promise.all([portfolioApi.getPortfolio(), portfolioApi.getMetrics()]);

      // Fetch live prices before rendering so metrics never flash $0
      if (portfolioData.positions.length > 0) {
        const tickers = portfolioData.positions.map((pos) => pos.ticker);
        try {
          const { stocksApi } = await import("@/app/lib/api/stocks");
          const prices = await stocksApi.getBatchPrices(tickers);
          portfolioData.positions = portfolioData.positions.map((pos) => {
            const price = prices[pos.ticker];
            const currentPrice = price?.price ?? pos.purchase_price;
            const currentValue = currentPrice * pos.quantity;
            const gainLoss = (currentPrice - pos.purchase_price) * pos.quantity;
            const gainLossPercent = pos.purchase_price > 0
              ? ((currentPrice - pos.purchase_price) / pos.purchase_price) * 100
              : 0;
            return { ...pos, current_price: currentPrice, current_value: currentValue, gain_loss: gainLoss, gain_loss_percent: gainLossPercent };
          });
        } catch {
          // Non-fatal: fall back to purchase price
        }
        // Subscribe happens automatically in WebSocket onConnected callback
      }

      // Override metrics with live-computed values from positions
      const liveValue = portfolioData.positions.reduce((s, p) => s + p.current_value, 0);
      const liveCost = portfolioData.positions.reduce((s, p) => s + p.purchase_price * p.quantity, 0);
      const liveGainLoss = liveValue - liveCost;
      const liveGainLossPercent = liveCost > 0 ? (liveGainLoss / liveCost) * 100 : 0;
      const liveDailyGainLoss = portfolioData.positions.reduce((s, p) => s + (p.gain_loss || 0), 0);

      setPortfolio(portfolioData);
      setMetrics({
        ...metricsData,
        total_value: liveValue,
        total_gain_loss: liveGainLoss,
        total_gain_loss_percent: liveGainLossPercent,
        daily_gain_loss: metricsData.daily_gain_loss !== 0 ? metricsData.daily_gain_loss : liveDailyGainLoss,
      });
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, [subscribe]);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    loadPortfolio();
  }, [loadPortfolio, user, authLoading]);

  // Auto-refresh disabled to prevent losing analysis modal
  // useDataRefresh(() => {
  //   if (!loading) {
  //     loadPortfolio();
  //   }
  // }, true);

  // Cleanup: unsubscribe from tickers when component unmounts
  useEffect(() => {
    return () => {
      if (portfolio?.positions) {
        const tickers = portfolio.positions.map((pos) => pos.ticker);
        unsubscribe(tickers);
      }
    };
  }, [portfolio, unsubscribe]);

  const handleDeletePosition = async (position: StockPosition) => {
    setDeletingPosition(position);
  };

  const confirmDelete = async () => {
    if (!deletingPosition) return;

    try {
      setIsDeleting(true);
      await portfolioApi.removePosition(deletingPosition.id);
      setDeletingPosition(null);
      await loadPortfolio();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsDeleting(false);
    }
  };

  const cancelDelete = () => {
    setDeletingPosition(null);
  };

  const handleEditPosition = (position: StockPosition) => {
    setEditingPosition(position);
    setShowAddModal(true);
  };

  const handleModalClose = () => {
    setShowAddModal(false);
    setEditingPosition(null);
  };

  const handleModalSuccess = () => {
    loadPortfolio();
  };

  const handleExport = async (format: "csv" | "excel") => {
    try {
      setIsExporting(true);
      setShowExportMenu(false);
      const blob = await portfolioApi.exportPortfolio(format);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `portfolio-export.${format === "csv" ? "csv" : "xlsx"}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      // Show success message
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 3000);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsExporting(false);
    }
  };

  const handleImportSuccess = () => {
    setShowImportModal(false);
    setImportSuccess(true);
    setTimeout(() => setImportSuccess(false), 3000);
    loadPortfolio();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Portfolio</h2>
          <p className="text-red-600">{error}</p>
          <button onClick={loadPortfolio} className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const totalValue = portfolio?.positions?.reduce((sum, p) => sum + (p.current_value || 0), 0) || 0;
  const totalCost = portfolio?.positions?.reduce((sum, p) => sum + (p.purchase_price * p.quantity), 0) || 0;
  const totalGainLoss = totalValue - totalCost;
  const totalGainLossPercent = totalCost > 0 ? (totalGainLoss / totalCost) * 100 : 0;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Portfolio</h1>
          <div className="flex items-center gap-2 mt-2">
            <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${isConnected ? "bg-green-900 text-green-300" : "bg-gray-800 text-gray-400"}`}>{isConnected ? "● Live" : "○ Offline"}</span>
          </div>
        </div>
        <div className="flex gap-3">
          {/* Import Button */}
          <button onClick={() => setShowImportModal(true)} className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Import
          </button>

          {/* Export Button with Dropdown */}
          <div className="relative export-menu-container">
            <button onClick={() => setShowExportMenu(!showExportMenu)} disabled={isExporting || !portfolio?.positions || portfolio.positions.length === 0} className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2">
              {isExporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Exporting...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Export
                </>
              )}
            </button>

            {/* Export Format Dropdown */}
            {showExportMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-[#1a1a1a] rounded-lg shadow-lg border border-[#2a2a2a] z-10">
                <div className="py-1">
                  <button onClick={() => handleExport("csv")} className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-[#2a2a2a] flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Export as CSV
                  </button>
                  <button onClick={() => handleExport("excel")} className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-[#2a2a2a] flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Export as Excel
                  </button>
                </div>
              </div>
            )}
          </div>

          <button onClick={() => setShowAddModal(true)} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
            + Add Stock
          </button>
        </div>
      </div>

      {/* Export Success Message */}
      {exportSuccess && (
        <div className="mb-4 bg-green-900/20 border border-green-800 rounded-lg p-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-green-300">Portfolio exported successfully!</span>
        </div>
      )}

      {/* Import Success Message */}
      {importSuccess && (
        <div className="mb-4 bg-green-900/20 border border-green-800 rounded-lg p-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-green-300">Portfolio imported successfully!</span>
        </div>
      )}

      {/* Portfolio Metrics */}
      {metrics && (
        <div className="mb-8">
          <PortfolioMetrics metrics={metrics} totalValue={totalValue} totalGainLoss={totalGainLoss} totalGainLossPercent={totalGainLossPercent} />
        </div>
      )}

      {/* Portfolio Analysis */}
      {portfolio && portfolio.positions.length > 0 && (
        <div className="mb-8">
          <PortfolioAnalysisPanel />
        </div>
      )}

      {/* Stock Positions */}
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-[#2a2a2a]">
          <h2 className="text-xl font-semibold text-white">Positions</h2>
        </div>

        {!portfolio?.positions || portfolio.positions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 mb-4">No positions yet</p>
            <button onClick={() => setShowAddModal(true)} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Add Your First Stock
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#111111]">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Ticker</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Quantity</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Purchase Price</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Current Price</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Current Value</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Gain/Loss</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-[#1a1a1a] divide-y divide-[#2a2a2a]">
                {portfolio.positions.map((position) => (
                  <tr key={position.id} className="hover:bg-[#222222]">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-white">{position.ticker}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-300">{position.quantity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-300">${position.purchase_price.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-300">${position.current_price.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-300">${position.current_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <div className={position.gain_loss >= 0 ? "text-green-600" : "text-red-600"}>
                        <div className="font-medium">
                          {position.gain_loss >= 0 ? "+" : ""}${position.gain_loss.toFixed(2)}
                        </div>
                        <div className="text-xs">
                          {position.gain_loss >= 0 ? "+" : ""}
                          {position.gain_loss_percent.toFixed(2)}%
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex gap-2 justify-end">
                        <button onClick={() => handleEditPosition(position)} className="text-blue-400 hover:text-blue-300">
                          Edit
                        </button>
                        <button onClick={() => handleDeletePosition(position)} className="text-red-400 hover:text-red-300">
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add/Edit Stock Modal */}
      <AddStockModal isOpen={showAddModal} onClose={handleModalClose} onSuccess={handleModalSuccess} editPosition={editingPosition} />

      {/* Import Portfolio Modal */}
      <ImportPortfolioModal isOpen={showImportModal} onClose={() => setShowImportModal(false)} onSuccess={handleImportSuccess} />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog isOpen={!!deletingPosition} title="Delete Position" message={`Are you sure you want to delete your ${deletingPosition?.ticker} position? This action cannot be undone.`} confirmLabel={isDeleting ? "Deleting..." : "Delete"} cancelLabel="Cancel" onConfirm={confirmDelete} onCancel={cancelDelete} isDestructive />
    </div>
  );
}
