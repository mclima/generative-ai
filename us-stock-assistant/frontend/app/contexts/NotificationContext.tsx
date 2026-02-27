"use client";

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { useWebSocket } from "@/app/hooks/useWebSocket";
import type { Notification } from "@/app/types/notifications";
import type { StockPrice } from "@/app/types/stocks";
import NotificationToast from "@/app/components/NotificationToast";

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Notification) => void;
  clearNotification: () => void;
  isConnected: boolean;
  subscribe: (tickers: string[]) => void;
  unsubscribe: (tickers: string[]) => void;
  onPriceUpdate: (callback: (data: StockPrice) => void) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

let priceUpdateCallback: ((data: StockPrice) => void) | null = null;

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [currentToast, setCurrentToast] = useState<Notification | null>(null);
  const [hasToken, setHasToken] = useState(false);

  // Check for token on mount and when storage changes
  useEffect(() => {
    const checkToken = () => {
      setHasToken(!!localStorage.getItem("access_token"));
    };
    checkToken();
    window.addEventListener("storage", checkToken);
    return () => window.removeEventListener("storage", checkToken);
  }, []);

  const handleNotification = useCallback((notification: Notification) => {
    setNotifications((prev) => [notification, ...prev]);
    setCurrentToast(notification);
  }, []);

  const handlePriceUpdate = useCallback((data: StockPrice) => {
    if (priceUpdateCallback) {
      priceUpdateCallback(data);
    }
  }, []);

  const { isConnected, subscribe, unsubscribe } = useWebSocket({
    enabled: hasToken,
    onNotification: handleNotification,
    onPriceUpdate: handlePriceUpdate,
    onConnected: () => {
      console.log("WebSocket connected");
    },
    onDisconnected: () => {
      console.log("WebSocket disconnected");
    },
    onError: (error) => {
      console.error("WebSocket error:", error);
    },
  });

  const addNotification = useCallback((notification: Notification) => {
    setNotifications((prev) => [notification, ...prev]);
    setCurrentToast(notification);
  }, []);

  const clearNotification = useCallback(() => {
    setCurrentToast(null);
  }, []);

  const registerPriceUpdateCallback = useCallback((callback: (data: StockPrice) => void) => {
    priceUpdateCallback = callback;
  }, []);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        addNotification,
        clearNotification,
        isConnected,
        subscribe,
        unsubscribe,
        onPriceUpdate: registerPriceUpdateCallback,
      }}>
      {children}
      <NotificationToast notification={currentToast} onClose={clearNotification} />
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error("useNotifications must be used within a NotificationProvider");
  }
  return context;
}
