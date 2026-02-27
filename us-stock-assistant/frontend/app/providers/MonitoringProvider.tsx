"use client";

/**
 * Monitoring Provider
 *
 * Initializes monitoring and performance tracking for the application.
 */

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { initWebVitals, trackPageView } from "../lib/monitoring";

export function MonitoringProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  useEffect(() => {
    // Initialize Web Vitals tracking
    initWebVitals();
  }, []);

  useEffect(() => {
    // Track page views on route changes
    if (pathname) {
      trackPageView(pathname);
    }
  }, [pathname]);

  return <>{children}</>;
}
