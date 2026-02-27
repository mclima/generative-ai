"use client";

import { useState, useEffect } from "react";

export type Orientation = "portrait" | "landscape";

interface DeviceOrientationState {
  orientation: Orientation;
  angle: number;
  isPortrait: boolean;
  isLandscape: boolean;
}

/**
 * Hook to detect and respond to device orientation changes
 * Useful for adjusting layouts when device is rotated
 */
export function useDeviceOrientation(): DeviceOrientationState {
  const [orientation, setOrientation] = useState<Orientation>("portrait");
  const [angle, setAngle] = useState(0);

  useEffect(() => {
    const handleOrientationChange = () => {
      // Check window dimensions
      const isPortrait = window.innerHeight > window.innerWidth;
      setOrientation(isPortrait ? "portrait" : "landscape");

      // Get screen orientation angle if available
      if (window.screen?.orientation) {
        setAngle(window.screen.orientation.angle);
      } else if (window.orientation !== undefined) {
        setAngle(window.orientation as number);
      }
    };

    // Set initial orientation
    handleOrientationChange();

    // Listen for orientation changes
    window.addEventListener("resize", handleOrientationChange);
    window.addEventListener("orientationchange", handleOrientationChange);

    return () => {
      window.removeEventListener("resize", handleOrientationChange);
      window.removeEventListener("orientationchange", handleOrientationChange);
    };
  }, []);

  return {
    orientation,
    angle,
    isPortrait: orientation === "portrait",
    isLandscape: orientation === "landscape",
  };
}

/**
 * Hook to get responsive breakpoint information
 */
export function useBreakpoint() {
  const [breakpoint, setBreakpoint] = useState<"xs" | "sm" | "md" | "lg" | "xl" | "2xl">("md");

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width < 640) setBreakpoint("xs");
      else if (width < 768) setBreakpoint("sm");
      else if (width < 1024) setBreakpoint("md");
      else if (width < 1280) setBreakpoint("lg");
      else if (width < 1536) setBreakpoint("xl");
      else setBreakpoint("2xl");
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return {
    breakpoint,
    isMobile: breakpoint === "xs" || breakpoint === "sm",
    isTablet: breakpoint === "md",
    isDesktop: breakpoint === "lg" || breakpoint === "xl" || breakpoint === "2xl",
  };
}
