"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Sparkles, Loader2, TrendingUp, AlertTriangle, Info } from "lucide-react";

interface AIInsightsProps {
  symbol: string;
  data?: AIInsightsData | null;
  isLoading?: boolean;
  onFetchInsights?: () => void;
  insightsRequested?: boolean;
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

export default function AIInsights({ symbol, data: initialData, isLoading: externalLoading, onFetchInsights, insightsRequested }: AIInsightsProps) {
  const [insights, setInsights] = useState<Insight[]>(initialData?.insights || []);
  const [summary, setSummary] = useState<string>(initialData?.summary || "");

  useEffect(() => {
    if (initialData) {
      setInsights(initialData.insights || []);
      setSummary(initialData.summary || "");
    }
  }, [initialData]);

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

  return (
    <div className="card h-full">
      <div className="flex items-center mb-4">
        <Sparkles className="w-6 h-6 text-purple-500 mr-2" />
        <h3 className="text-xl font-semibold">AI Insights</h3>
      </div>

      {!insightsRequested ? (
        <div className="flex flex-col items-center justify-center py-12">
          <Sparkles className="w-12 h-12 text-purple-500 mb-4 opacity-50" />
          <p className="text-gray-400 mb-4 text-center">Generate AI-powered insights for {symbol}</p>
          <button
            onClick={onFetchInsights}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 rounded-lg font-semibold transition-all transform hover:scale-105 flex items-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            Generate AI Insights
          </button>
          <p className="text-xs text-gray-500 mt-3">Takes ~7-10 seconds</p>
        </div>
      ) : externalLoading ? (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary mb-3" />
          <p className="text-sm text-gray-400">Generating insights...</p>
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
