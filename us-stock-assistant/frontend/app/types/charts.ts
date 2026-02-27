/**
 * Time range options for chart displays
 */
export type TimeRange = "1D" | "1W" | "1M" | "3M" | "1Y" | "ALL";

/**
 * Chart type options
 */
export type ChartType = "line" | "candlestick" | "bar" | "pie";

/**
 * Data point for portfolio value over time
 */
export interface PortfolioValueDataPoint {
  date: string;
  value: number;
  timestamp: number;
}

/**
 * Data point for portfolio composition
 */
export interface PortfolioCompositionDataPoint {
  ticker: string;
  value: number;
  percentage: number;
  color?: string;
}

/**
 * Data point for stock price history (candlestick)
 */
export interface StockPriceDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  timestamp: number;
}

/**
 * Data point for simple line chart
 */
export interface LineChartDataPoint {
  date: string;
  value: number;
  timestamp: number;
}
