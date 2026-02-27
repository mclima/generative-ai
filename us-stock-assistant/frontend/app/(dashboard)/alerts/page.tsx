"use client";

import { useState, useEffect } from "react";
import { alertsApi } from "@/app/lib/api/alerts";
import { handleApiError } from "@/app/lib/api-client";
import type { PriceAlert } from "@/app/types/alerts";
import AlertModal from "@/app/components/AlertModal";
import ConfirmDialog from "@/app/components/ConfirmDialog";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState<PriceAlert | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; alertId: string | null }>({
    isOpen: false,
    alertId: null,
  });
  const [filter, setFilter] = useState<"all" | "active" | "triggered">("all");

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await alertsApi.getAlerts();
      setAlerts(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateAlert = () => {
    setEditingAlert(null);
    setIsModalOpen(true);
  };

  const handleEditAlert = (alert: PriceAlert) => {
    setEditingAlert(alert);
    setIsModalOpen(true);
  };

  const handleDeleteAlert = async (id: string) => {
    try {
      await alertsApi.deleteAlert(id);
      await loadAlerts();
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const handleModalSuccess = () => {
    loadAlerts();
  };

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === "active") return alert.is_active && !alert.triggered_at;
    if (filter === "triggered") return alert.triggered_at;
    return true;
  });

  const activeAlerts = alerts.filter((a) => a.is_active && !a.triggered_at);
  const triggeredAlerts = alerts.filter((a) => a.triggered_at);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-white">Price Alerts</h1>
            <p className="text-gray-400 mt-1">Manage your stock price alerts and notifications</p>
          </div>
          <button onClick={handleCreateAlert} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Alert
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 rounded-lg shadow">
            <div className="text-sm text-gray-400">Total Alerts</div>
            <div className="text-2xl font-bold text-white">{alerts.length}</div>
          </div>
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 rounded-lg shadow">
            <div className="text-sm text-gray-400">Active Alerts</div>
            <div className="text-2xl font-bold text-green-600">{activeAlerts.length}</div>
          </div>
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-4 rounded-lg shadow">
            <div className="text-sm text-gray-400">Triggered</div>
            <div className="text-2xl font-bold text-orange-600">{triggeredAlerts.length}</div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6 border-b border-[#2a2a2a]">
        <nav className="flex space-x-8">
          <button onClick={() => setFilter("all")} className={`py-4 px-1 border-b-2 font-medium text-sm ${filter === "all" ? "border-blue-500 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-300 hover:border-gray-600"}`}>
            All Alerts ({alerts.length})
          </button>
          <button onClick={() => setFilter("active")} className={`py-4 px-1 border-b-2 font-medium text-sm ${filter === "active" ? "border-blue-500 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-300 hover:border-gray-600"}`}>
            Active ({activeAlerts.length})
          </button>
          <button onClick={() => setFilter("triggered")} className={`py-4 px-1 border-b-2 font-medium text-sm ${filter === "triggered" ? "border-blue-500 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-300 hover:border-gray-600"}`}>
            Triggered ({triggeredAlerts.length})
          </button>
        </nav>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredAlerts.length === 0 ? (
        /* Empty State */
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-white">No alerts</h3>
          <p className="mt-1 text-sm text-gray-500">{filter === "all" ? "Get started by creating your first price alert." : `No ${filter} alerts found.`}</p>
          {filter === "all" && (
            <div className="mt-6">
              <button onClick={handleCreateAlert} className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Alert
              </button>
            </div>
          )}
        </div>
      ) : (
        /* Alerts List */
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow overflow-hidden">
          <div className="divide-y divide-[#2a2a2a]">
            {filteredAlerts.map((alert) => (
              <div key={alert.id} className="p-6 hover:bg-[#222222]">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-lg font-bold text-white">{alert.ticker}</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${alert.triggered_at ? "bg-orange-900/20 text-orange-400" : alert.is_active ? "bg-green-900/20 text-green-400" : "bg-[#2a2a2a] text-gray-400"}`}>{alert.triggered_at ? "Triggered" : alert.is_active ? "Active" : "Inactive"}</span>
                    </div>
                    <div className="text-sm text-gray-400 mb-2">
                      Alert when price goes <span className="font-medium text-white">{alert.condition}</span> <span className="font-medium text-white">${alert.target_price.toFixed(2)}</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>Created: {new Date(alert.created_at).toLocaleDateString()}</span>
                      {alert.triggered_at && <span>Triggered: {new Date(alert.triggered_at).toLocaleDateString()}</span>}
                      <div className="flex items-center gap-1">
                        <span>Channels:</span>
                        {alert.notification_channels.map((channel) => (
                          <span key={channel} className="px-2 py-0.5 bg-[#2a2a2a] rounded text-gray-400">
                            {channel}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <button onClick={() => handleEditAlert(alert)} className="p-2 text-gray-400 hover:text-blue-400 rounded-lg hover:bg-blue-900/20" title="Edit alert">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button onClick={() => setDeleteConfirm({ isOpen: true, alertId: alert.id })} className="p-2 text-gray-400 hover:text-red-400 rounded-lg hover:bg-red-900/20" title="Delete alert">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Alert Modal */}
      <AlertModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onSuccess={handleModalSuccess} editAlert={editingAlert} />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        title="Delete Alert"
        message="Are you sure you want to delete this alert? This action cannot be undone."
        confirmLabel="Delete"
        isDestructive={true}
        onConfirm={() => {
          if (deleteConfirm.alertId) {
            handleDeleteAlert(deleteConfirm.alertId);
          }
          setDeleteConfirm({ isOpen: false, alertId: null });
        }}
        onCancel={() => setDeleteConfirm({ isOpen: false, alertId: null })}
      />
    </div>
  );
}
