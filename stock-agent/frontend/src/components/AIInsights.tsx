"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Sparkles, Loader2, TrendingUp, AlertTriangle, Info } from "lucide-react";

interface AIInsightsProps {
  symbol: string;
  data?: AIInsightsData | null;
  isLoading?: boolean;
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

export default function AIInsights({ symbol, data: initialData, isLoading: externalLoading }: AIInsightsProps) {
  const [insights, setInsights] = useState<Insight[]>(initialData?.insights || []);
  const [summary, setSummary] = useState<string>(initialData?.summary || "");
  const [loading, setLoading] = useState(!initialData);

  useEffect(() => {
    if (initialData) {
      setInsights(initialData.insights || []);
      setSummary(initialData.summary || "");
      setLoading(false);
      return;
    }

    const fetchInsights = async () => {
      setLoading(true);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await axios.get(`${apiUrl}/api/stock/${symbol}/insights`);
        setInsights(response.data.insights || []);
        setSummary(response.data.summary || "");
      } catch (err) {
        console.error("Failed to fetch AI insights:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [symbol, initialData]);

  const getIcon = (type: string) => {
    switch (type) {
      case "bullish":
        return <TrendingUp className="w-5 h-5 text-success" />;
      case "bearish":
        return <AlertTriangle className="w-5 h-5 text-danger" />;
      default:
        return <Info className="w-5 h-5 text-info" />;
    }
  };

  const isLoading = externalLoading !== undefined ? externalLoading : loading;

  return (
    <div className="card h-full">
      <div className="flex items-center mb-4">
        <Sparkles className="w-6 h-6 text-purple-500 mr-2" />
        <h3 className="text-xl font-semibold">AI Insights</h3>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="space-y-4">
          {summary && (
            <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-800/50 rounded-lg p-4">
              <p className="text-sm leading-relaxed">{summary}</p>
            </div>
          )}

          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div
                key={index}
                className="bg-gray-800/50 rounded-lg p-4 border border-gray-700"
              >
                <div className="flex items-start">
                  <div className="mr-3 mt-1">{getIcon(insight.type)}</div>
                  <div>
                    <h4 className="font-semibold mb-1">{insight.title}</h4>
                    <p className="text-sm text-gray-400">{insight.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-800">
            <p className="text-xs text-gray-500 flex items-center">
              <Sparkles className="w-3 h-3 mr-1" />
              Powered by OpenAI GPT-4o-mini
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
