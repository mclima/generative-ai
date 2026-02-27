export interface UserPreferences {
  default_chart_type: "line" | "candlestick";
  default_time_range: "1D" | "1W" | "1M" | "3M" | "1Y" | "ALL";
  preferred_news_sources: string[];
  notification_settings: NotificationSettings;
  refresh_interval: number;
}

export interface NotificationSettings {
  in_app: boolean;
  email: boolean;
  push: boolean;
  alert_types: {
    price_alerts: boolean;
    news_updates: boolean;
    portfolio_changes: boolean;
  };
}

export interface PreferencesUpdateInput {
  default_chart_type?: "line" | "candlestick";
  default_time_range?: "1D" | "1W" | "1M" | "3M" | "1Y" | "ALL";
  preferred_news_sources?: string[];
  notification_settings?: NotificationSettings;
  refresh_interval?: number;
}
