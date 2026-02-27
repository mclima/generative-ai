export interface PriceAlertInput {
  ticker: string;
  condition: "above" | "below";
  target_price: number;
  notification_channels: ("in-app" | "email" | "push")[];
}

export interface PriceAlert extends PriceAlertInput {
  id: string;
  user_id: string;
  is_active: boolean;
  created_at: string;
  triggered_at?: string;
}
