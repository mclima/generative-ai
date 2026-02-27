/**
 * Frontend monitoring utilities
 *
 * Provides functions for tracking user interactions, performance metrics,
 * and custom events using console logging for development.
 */

import { onCLS, onFID, onFCP, onLCP, onTTFB, Metric } from "web-vitals";

/**
 * Track Core Web Vitals
 */
export function initWebVitals() {
  const logMetric = (metric: Metric) => {
    // Log for debugging
    if (process.env.NODE_ENV === "development") {
      console.log(`[Web Vitals] ${metric.name}:`, metric.value, metric.rating);
    }
  };

  // Initialize web vitals tracking
  onCLS(logMetric);
  onFID(logMetric);
  onFCP(logMetric);
  onLCP(logMetric);
  onTTFB(logMetric);
}

/**
 * Track user interactions
 */
export function trackUserInteraction(action: string, category: string, label?: string, value?: number) {
  if (process.env.NODE_ENV === "development") {
    console.log(`[User Interaction] ${category}:${action}`, { label, value });
  }
}

/**
 * Track API errors
 */
export function trackApiError(endpoint: string, error: Error, statusCode?: number) {
  console.error(`[API Error] ${endpoint}:`, {
    error: error.message,
    statusCode,
    stack: error.stack,
  });
}

/**
 * Track custom events
 */
export function trackEvent(eventName: string, data?: Record<string, any>) {
  if (process.env.NODE_ENV === "development") {
    console.log(`[Custom Event] ${eventName}`, data);
  }
}

/**
 * Track page views
 */
export function trackPageView(pageName: string, properties?: Record<string, any>) {
  if (process.env.NODE_ENV === "development") {
    console.log(`[Page View] ${pageName}`, properties);
  }
}

/**
 * Track performance metrics
 */
export function trackPerformance(metricName: string, value: number, unit: string = "ms") {
  if (process.env.NODE_ENV === "development") {
    console.log(`[Performance] ${metricName}: ${value}${unit}`);
  }
}

/**
 * Set user context for error tracking
 */
export function setUserContext(userId: string, email?: string) {
  if (process.env.NODE_ENV === "development") {
    console.log(`[User Context] Set user:`, { userId, email });
  }
}

/**
 * Clear user context (on logout)
 */
export function clearUserContext() {
  if (process.env.NODE_ENV === "development") {
    console.log(`[User Context] Cleared user context`);
  }
}

/**
 * Track component render time
 */
export function trackComponentRender(componentName: string, renderTime: number) {
  trackPerformance(`component_render_${componentName}`, renderTime);
}

/**
 * Track data fetch time
 */
export function trackDataFetch(dataSource: string, fetchTime: number, success: boolean) {
  trackPerformance(`data_fetch_${dataSource}`, fetchTime);

  trackEvent("data_fetch", {
    source: dataSource,
    duration_ms: fetchTime,
    success,
  });
}

/**
 * Track chart render time
 */
export function trackChartRender(chartType: string, dataPoints: number, renderTime: number) {
  trackPerformance(`chart_render_${chartType}`, renderTime);

  trackEvent("chart_render", {
    chart_type: chartType,
    data_points: dataPoints,
    duration_ms: renderTime,
  });
}

/**
 * Track portfolio operations
 */
export function trackPortfolioOperation(operation: string, success: boolean, duration?: number) {
  trackEvent("portfolio_operation", {
    operation,
    success,
    duration_ms: duration,
  });
}

/**
 * Track stock search
 */
export function trackStockSearch(query: string, resultsCount: number, duration: number) {
  trackEvent("stock_search", {
    query_length: query.length,
    results_count: resultsCount,
    duration_ms: duration,
  });
}

/**
 * Track alert creation
 */
export function trackAlertCreation(alertType: string, success: boolean) {
  trackEvent("alert_creation", {
    alert_type: alertType,
    success,
  });
}

/**
 * Track news interaction
 */
export function trackNewsInteraction(action: string, articleId?: string) {
  trackUserInteraction(action, "news", articleId);
}

/**
 * Track chart interaction
 */
export function trackChartInteraction(action: string, chartType: string) {
  trackUserInteraction(action, "chart", chartType);
}
