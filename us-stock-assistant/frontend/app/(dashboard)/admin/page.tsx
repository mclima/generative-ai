"use client";

/**
 * Admin Dashboard Page
 *
 * Displays system metrics, monitoring data, and operational insights.
 */

import { useEffect, useState } from "react";
import axios from "axios";
import { trackPageView } from "@/app/lib/monitoring";

interface SystemMetrics {
  timestamp: string;
  users: {
    total: number;
    last_24h: number;
    last_7d: number;
  };
  portfolios: {
    total: number;
    total_positions: number;
    avg_positions_per_portfolio: number;
  };
  alerts: {
    total: number;
    active: number;
    triggered_last_24h: number;
  };
  notifications: {
    total: number;
    unread: number;
  };
  redis: {
    memory_mb: number;
    keys: number;
    connected_clients: number;
  };
}

interface MCPStatus {
  timestamp: string;
  servers: Array<{
    name: string;
    status: string;
    uptime_percent: number;
    requests_24h: number;
    avg_latency_ms: number;
    error_rate: number;
    last_error: string | null;
  }>;
}

interface AgentTaskStatus {
  timestamp: string;
  period_hours: number;
  agents: Array<{
    type: string;
    tasks_executed: number;
    tasks_succeeded: number;
    tasks_failed: number;
    avg_duration_ms: number;
    last_execution: string;
  }>;
  total_tasks: number;
  success_rate: number;
}

interface APIUsage {
  timestamp: string;
  period_hours: number;
  endpoints: Array<{
    endpoint: string;
    method: string;
    requests: number;
    avg_latency_ms: number;
    error_rate: number;
  }>;
  total_requests: number;
  avg_latency_ms: number;
  overall_error_rate: number;
}

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [mcpStatus, setMcpStatus] = useState<MCPStatus | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentTaskStatus | null>(null);
  const [apiUsage, setApiUsage] = useState<APIUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    trackPageView("admin_dashboard");
    fetchData();

    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const token = localStorage.getItem("access_token");

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      const [metricsRes, mcpRes, agentRes, apiRes] = await Promise.all([axios.get(`${apiUrl}/admin/metrics`, { headers }), axios.get(`${apiUrl}/admin/mcp-status`, { headers }), axios.get(`${apiUrl}/admin/agent-tasks`, { headers }), axios.get(`${apiUrl}/admin/api-usage`, { headers })]);

      setMetrics(metricsRes.data);
      setMcpStatus(mcpRes.data);
      setAgentStatus(agentRes.data);
      setApiUsage(apiRes.data);
    } catch (err: any) {
      console.error("Failed to fetch admin data:", err);
      setError(err.response?.data?.detail || "Failed to load admin dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (loading && !metrics) {
    return (
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">{error}</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <button onClick={fetchData} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Refresh
        </button>
      </div>

      {/* System Metrics */}
      {metrics && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">System Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard title="Total Users" value={metrics.users.total} subtitle={`+${metrics.users.last_24h} today, +${metrics.users.last_7d} this week`} />
            <MetricCard title="Portfolios" value={metrics.portfolios.total} subtitle={`${metrics.portfolios.total_positions} positions total`} />
            <MetricCard title="Active Alerts" value={metrics.alerts.active} subtitle={`${metrics.alerts.triggered_last_24h} triggered today`} />
            <MetricCard title="Redis Memory" value={`${metrics.redis.memory_mb} MB`} subtitle={`${metrics.redis.keys} keys, ${metrics.redis.connected_clients} clients`} />
          </div>
        </div>
      )}

      {/* API Usage */}
      {apiUsage && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">API Usage (Last 24h)</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Endpoint</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requests</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Latency</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Error Rate</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {apiUsage.endpoints.map((endpoint, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {endpoint.method} {endpoint.endpoint}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{endpoint.requests.toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{endpoint.avg_latency_ms}ms</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded ${endpoint.error_rate < 0.01 ? "bg-green-100 text-green-800" : endpoint.error_rate < 0.05 ? "bg-yellow-100 text-yellow-800" : "bg-red-100 text-red-800"}`}>{(endpoint.error_rate * 100).toFixed(2)}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MCP Server Status */}
      {mcpStatus && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">MCP Server Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {mcpStatus.servers.map((server, idx) => (
              <div key={idx} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">{server.name}</h3>
                  <span className={`px-3 py-1 rounded-full text-sm ${server.status === "healthy" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>{server.status}</span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Uptime:</span>
                    <span className="font-medium">{server.uptime_percent}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Requests (24h):</span>
                    <span className="font-medium">{server.requests_24h.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Latency:</span>
                    <span className="font-medium">{server.avg_latency_ms}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Error Rate:</span>
                    <span className="font-medium">{(server.error_rate * 100).toFixed(2)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Task Status */}
      {agentStatus && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Agent Task Execution (Last 24h)</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Executed</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Success Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Duration</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Execution</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {agentStatus.agents.map((agent, idx) => {
                  const successRate = (agent.tasks_succeeded / agent.tasks_executed) * 100;
                  return (
                    <tr key={idx}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{agent.type}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{agent.tasks_executed}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 py-1 rounded ${successRate >= 99 ? "bg-green-100 text-green-800" : successRate >= 95 ? "bg-yellow-100 text-yellow-800" : "bg-red-100 text-red-800"}`}>{successRate.toFixed(1)}%</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{agent.avg_duration_ms}ms</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(agent.last_execution).toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, subtitle }: { title: string; value: string | number; subtitle?: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-600 mb-2">{title}</h3>
      <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
    </div>
  );
}
