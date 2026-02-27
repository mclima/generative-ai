export interface SentimentScore {
  label: "positive" | "negative" | "neutral";
  score: number; // -1 to 1
  confidence: number; // 0 to 1
}

export interface NewsArticle {
  id: string;
  headline: string;
  source: string;
  url: string;
  published_at: string;
  summary: string;
  sentiment?: SentimentScore;
}

export interface StockSentiment {
  ticker: string;
  overall_sentiment: SentimentScore;
  article_count: number;
  recent_articles: NewsArticle[];
}
