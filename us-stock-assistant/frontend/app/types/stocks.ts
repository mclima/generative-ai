export interface StockPrice {
  ticker: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
}

export interface HistoricalData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockSearchResult {
  ticker: string;
  company_name: string;
  exchange: string;
  relevance_score: number;
}

export interface CompanyInfo {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  market_cap: number;
  description: string;
}

export interface FinancialMetrics {
  ticker: string;
  pe_ratio: number;
  eps: number;
  dividend_yield: number;
  beta: number;
  fifty_two_week_high: number;
  fifty_two_week_low: number;
}
