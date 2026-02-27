export interface StockAnalysis {
  ticker: string;
  summary: string;
  price_analysis: {
    trend: "bullish" | "bearish" | "neutral";
    support: number;
    resistance: number;
    volatility: "high" | "medium" | "low";
  };
  sentiment_analysis: {
    overall: "positive" | "negative" | "neutral";
    score: number;
    news_count: number;
  };
  recommendations: string[];
  risks: string[];
  generated_at: string;
}

export interface PortfolioAnalysis {
  overall_health: "good" | "fair" | "poor";
  diversification_score: number;
  risk_level: "high" | "medium" | "low";
  rebalancing_suggestions: RebalancingSuggestion[];
  underperforming_stocks: string[];
  opportunities: string[];
}

export interface RebalancingSuggestion {
  action: "buy" | "sell" | "hold";
  ticker: string;
  reason: string;
  suggested_amount: number;
}
