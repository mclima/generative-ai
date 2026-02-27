"use client";

import { useState } from "react";
import type { SentimentScore } from "@/app/types/news";
import type { SentimentEvaluation, MarketIndex } from "@/app/types/market";
import { marketApi } from "@/app/lib/api/market";
import { handleApiError } from "@/app/lib/api-client";

interface MarketSentimentProps {
  sentiment: SentimentScore;
  indices: MarketIndex[];
}

export default function MarketSentiment({ sentiment, indices }: MarketSentimentProps) {
  const [evaluation, setEvaluation] = useState<SentimentEvaluation | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEvaluation, setShowEvaluation] = useState(false);

  // Calculate News-Market alignment
  const calculateAlignment = () => {
    if (!indices || indices.length === 0) {
      return { strength: "unknown", description: "No market data available" };
    }

    const avgMarketChange = indices.reduce((sum, idx) => sum + idx.change_percent, 0) / indices.length;
    const newsDirection = sentiment.score > 0.1 ? "positive" : sentiment.score < -0.1 ? "negative" : "neutral";
    const marketDirection = avgMarketChange > 0.1 ? "positive" : avgMarketChange < -0.1 ? "negative" : "neutral";

    if (newsDirection === marketDirection && newsDirection !== "neutral") {
      return { 
        strength: "Strong Alignment", 
        description: `News sentiment and market movement both ${newsDirection}`,
        color: "text-green-400"
      };
    } else if (newsDirection !== "neutral" && marketDirection !== "neutral" && newsDirection !== marketDirection) {
      return { 
        strength: "Misaligned", 
        description: `News is ${newsDirection} but market is ${marketDirection}`,
        color: "text-yellow-400"
      };
    } else {
      return { 
        strength: "Neutral", 
        description: "Mixed signals from news and market",
        color: "text-gray-400"
      };
    }
  };

  const alignment = calculateAlignment();

  const handleEvaluate = async () => {
    setIsEvaluating(true);
    setError(null);
    try {
      const result = await marketApi.evaluateMarketSentiment();
      setEvaluation(result);
      setShowEvaluation(true);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsEvaluating(false);
    }
  };

  const getAccuracyColor = (accuracy: string) => {
    if (accuracy.includes("Highly Accurate")) return "text-green-400";
    if (accuracy.includes("Moderately Accurate")) return "text-blue-400";
    if (accuracy.includes("Somewhat Inaccurate")) return "text-yellow-400";
    if (accuracy.includes("Highly Inaccurate")) return "text-red-400";
    return "text-gray-400";
  };

  const getSentimentColor = (label: string) => {
    switch (label) {
      case "positive":
        return "bg-green-900/20 border-green-700 text-green-400";
      case "negative":
        return "bg-red-900/20 border-red-700 text-red-400";
      case "neutral":
      default:
        return "bg-[#111111] border-[#2a2a2a] text-gray-400";
    }
  };

  const getSentimentIcon = (label: string) => {
    switch (label) {
      case "positive":
        return (
          <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
          </svg>
        );
      case "negative":
        return (
          <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
          </svg>
        );
      case "neutral":
      default:
        return (
          <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  const getSentimentDescription = (label: string, score: number) => {
    const absScore = Math.abs(score);
    if (label === "positive") {
      if (absScore > 0.7) return "Strongly Positive";
      if (absScore > 0.4) return "Moderately Positive";
      return "Slightly Positive";
    }
    if (label === "negative") {
      if (absScore > 0.7) return "Strongly Negative";
      if (absScore > 0.4) return "Moderately Negative";
      return "Slightly Negative";
    }
    return "Neutral";
  };

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">Overall Market Sentiment</h2>
        <button
          onClick={handleEvaluate}
          disabled={isEvaluating}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center gap-2"
        >
          {isEvaluating ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Evaluating...
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Evaluate with AI
            </>
          )}
        </button>
      </div>

      <div className={`border-2 rounded-lg p-6 ${getSentimentColor(sentiment.label)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {getSentimentIcon(sentiment.label)}
            <div>
              <p className="text-2xl font-bold capitalize">{getSentimentDescription(sentiment.label, sentiment.score)}</p>
              <p className="text-sm opacity-75 mt-1">Based on recent market news and analysis</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-4xl font-bold">{sentiment.score.toFixed(2)}</p>
            <p className="text-sm opacity-75">Sentiment Score</p>
            <p className="text-xs opacity-60 mt-1">Range: -1.0 to +1.0 | Confidence: {(sentiment.confidence * 100).toFixed(0)}%</p>
          </div>
        </div>

        {/* News-Market Alignment Indicator */}
        <div className="mt-4 pt-4 border-t border-current border-opacity-20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="h-4 w-4 opacity-75" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span className="text-sm font-medium opacity-75">News-Market Alignment:</span>
            </div>
            <div className="text-right">
              <span className={`text-sm font-semibold capitalize ${alignment.color}`}>
                {alignment.strength}
              </span>
              <p className="text-xs opacity-60 mt-0.5">{alignment.description}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="mt-4 bg-red-900/20 border border-red-800 rounded-lg p-4">
          <div className="flex items-start">
            <svg className="h-5 w-5 text-red-400 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-400 mb-1">Evaluation Failed</h3>
              <p className="text-sm text-red-400">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* LLM Evaluation Results */}
      {showEvaluation && evaluation && (
        <div className="mt-4 bg-[#111111] border border-[#2a2a2a] rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <svg className="h-5 w-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              AI Evaluation
            </h3>
            <button
              onClick={() => setShowEvaluation(false)}
              className="text-gray-400 hover:text-gray-300"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Evaluation Summary */}
          <div className="mb-4 p-4 bg-[#1a1a1a] rounded-lg border border-[#2a2a2a]">
            <p className="text-gray-300 text-sm leading-relaxed">{evaluation.llm_evaluation}</p>
          </div>

          {/* Accuracy Assessment */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[#2a2a2a]">
              <p className="text-xs text-gray-400 mb-1">Accuracy Assessment</p>
              <p className={`text-lg font-semibold ${getAccuracyColor(evaluation.accuracy_assessment)}`}>
                {evaluation.accuracy_assessment}
              </p>
            </div>
            <div className="p-4 bg-[#1a1a1a] rounded-lg border border-[#2a2a2a]">
              <p className="text-xs text-gray-400 mb-1">Confidence Level</p>
              <p className="text-lg font-semibold text-white">{evaluation.confidence_level}</p>
            </div>
          </div>

          {/* Recommendations */}
          {evaluation.recommendations.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-white mb-2">Recommendations for Improvement:</h4>
              <ul className="space-y-2">
                {evaluation.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start text-sm text-gray-300">
                    <svg className="h-4 w-4 text-purple-400 mr-2 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
