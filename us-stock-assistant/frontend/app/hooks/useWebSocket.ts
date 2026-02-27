"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { StockPrice } from "@/app/types/stocks";

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  enabled?: boolean;
  onPriceUpdate?: (data: StockPrice) => void;
  onNotification?: (notification: any) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: Error) => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      console.warn("No access token available for WebSocket connection");
      return;
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    const url = `${wsUrl}/ws?token=${token}`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebSocket opened");
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          switch (message.type) {
            case "connected":
              console.log("WebSocket connected");
              setConnectionId(message.connection_id);
              setIsConnected(true);
              options.onConnected?.();
              break;

            case "price_update":
              const priceData: StockPrice = {
                ticker: message.ticker,
                price: message.price,
                change: message.change,
                change_percent: message.changePercent,
                volume: message.volume,
                timestamp: message.timestamp,
              };
              options.onPriceUpdate?.(priceData);
              break;

            case "notification":
              options.onNotification?.(message.notification);
              break;

            case "error":
              console.error("WebSocket error message:", message.message);
              options.onError?.(new Error(message.message));
              break;

            case "pong":
              // Heartbeat response
              break;

            case "subscription_confirmed":
            case "unsubscription_confirmed":
              // Subscription acknowledgments - no action needed
              break;

            default:
              console.warn("Unknown WebSocket message type:", message.type);
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        options.onError?.(new Error("WebSocket connection error"));
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setIsConnected(false);
        setConnectionId(null);
        wsRef.current = null;
        options.onDisconnected?.();

        // Reconnection temporarily disabled to prevent connection spam
        // if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        //   reconnectAttemptsRef.current++;
        //   const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
        //   console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`);
        //   reconnectTimeoutRef.current = setTimeout(connect, delay);
        // }
      };
    } catch (error) {
      console.error("Error creating WebSocket:", error);
      options.onError?.(error as Error);
    }
  }, [options]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setConnectionId(null);
  }, []);

  const subscribe = useCallback(
    (tickers: string[]) => {
      if (wsRef.current && isConnected) {
        wsRef.current.send(
          JSON.stringify({
            action: "subscribe",
            tickers,
          }),
        );
      }
    },
    [isConnected],
  );

  const unsubscribe = useCallback(
    (tickers: string[]) => {
      if (wsRef.current && isConnected) {
        wsRef.current.send(
          JSON.stringify({
            action: "unsubscribe",
            tickers,
          }),
        );
      }
    },
    [isConnected],
  );

  const sendPing = useCallback(() => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({ action: "ping" }));
    }
  }, [isConnected]);

  useEffect(() => {
    const enabled = options.enabled !== false;
    const token = localStorage.getItem("access_token");
    if (enabled && token) {
      connect();
    }

    const heartbeatInterval = setInterval(sendPing, 30000);

    return () => {
      clearInterval(heartbeatInterval);
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options.enabled]); // Reconnect when enabled changes

  return {
    isConnected,
    connectionId,
    subscribe,
    unsubscribe,
    reconnect: connect,
  };
}
