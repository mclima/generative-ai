export interface Notification {
  id: string;
  user_id: string;
  type: "price_alert" | "news_update" | "portfolio_change";
  title: string;
  message: string;
  data: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

export interface NotificationGroup {
  type: string;
  count: number;
  notifications: Notification[];
  latestTimestamp: string;
}
