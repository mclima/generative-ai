import type { NewsArticle, SentimentScore } from "./news";

export interface MarketOverview {
  headlines: NewsArticle[];
  sentiment: SentimentScore;
  trending_tickers: TrendingTicker[];
  indices: MarketIndex[];
  sector_heatmap?: SectorPerformance[];
  last_updated: string;
}

export interface SentimentEvaluation {
  calculated_sentiment: SentimentScore;
  llm_evaluation: string;
  accuracy_assessment: string;
  confidence_level: string;
  recommendations: string[];
}

export interface TrendingTicker {
  ticker: string;
  company_name: string;
  price: number;
  change_percent: number;
  volume: number;
  news_count: number;
  reason: string;
}

export interface SectorPerformance {
  sector: string;
  change_percent: number;
  top_performers: string[];
  bottom_performers: string[];
}

export interface MarketIndex {
  name: string;
  symbol: string;
  value: number;
  change: number;
  change_percent: number;
}
