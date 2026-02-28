"use client";

import React from "react";
import { ResponsiveContainer } from "recharts";
import { useDeviceOrientation, useBreakpoint } from "@/app/hooks/useDeviceOrientation";

interface ChartWrapperProps {
  children: React.ReactElement;
  height?: number | string;
  className?: string;
  mobileHeight?: number;
  tabletHeight?: number;
}

/**
 * Reusable chart wrapper component that provides responsive sizing
 * and consistent styling for all charts. Adapts to device orientation.
 */
export const ChartWrapper: React.FC<ChartWrapperProps> = ({ children, height = 400, mobileHeight, tabletHeight, className = "" }) => {
  const { isPortrait } = useDeviceOrientation();
  const { isMobile, isTablet } = useBreakpoint();

  // Calculate responsive height based on device and orientation
  const getResponsiveHeight = () => {
    if (isMobile) {
      const baseHeight = mobileHeight || 300;
      // Reduce height in landscape mode on mobile
      return isPortrait ? baseHeight : baseHeight * 0.7;
    }
    if (isTablet) {
      const baseHeight = tabletHeight || 350;
      // Adjust height for tablet orientation
      return isPortrait ? baseHeight : baseHeight * 0.85;
    }
    return height;
  };

  const [responsiveHeight, setResponsiveHeight] = React.useState(height);

  React.useEffect(() => {
    setResponsiveHeight(getResponsiveHeight());
  }, [isPortrait, isMobile, isTablet, height, mobileHeight, tabletHeight]);

  return (
    <div className={`w-full ${className}`}>
      <ResponsiveContainer width="100%" height={responsiveHeight}>
        {children}
      </ResponsiveContainer>
    </div>
  );
};
