export interface StockPositionInput {
  ticker: string;
  quantity: number;
  purchase_price: number;
  purchase_date: string;
}

export interface StockPosition extends StockPositionInput {
  id: string;
  current_price: number;
  current_value: number;
  gain_loss: number;
  gain_loss_percent: number;
}

export interface Portfolio {
  id: string;
  user_id: string;
  positions: StockPosition[];
  total_value: number;
  total_gain_loss: number;
  total_gain_loss_percent: number;
  created_at: string;
  updated_at: string;
}

export interface PortfolioMetrics {
  total_value: number;
  total_gain_loss: number;
  total_gain_loss_percent: number;
  daily_gain_loss: number;
  diversity_score: number;
  performance_by_period: {
    "1D": number;
    "1W": number;
    "1M": number;
    "3M": number;
    "1Y": number;
    ALL: number;
  };
}
