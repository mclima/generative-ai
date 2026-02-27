"use client";

import React from "react";
import { useDeviceOrientation, useBreakpoint } from "@/app/hooks/useDeviceOrientation";

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Layout component that adapts to device orientation and screen size
 * Automatically adjusts spacing and layout when device is rotated
 */
export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ children, className = "" }) => {
  const { isPortrait, isLandscape } = useDeviceOrientation();
  const { isMobile, isTablet } = useBreakpoint();

  // Adjust padding based on orientation and device type
  const getPadding = () => {
    if (isMobile) {
      return isPortrait ? "p-4" : "p-3";
    }
    if (isTablet) {
      return isPortrait ? "p-6" : "p-4";
    }
    return "p-8";
  };

  return (
    <div className={`${getPadding()} ${className}`} data-orientation={isPortrait ? "portrait" : "landscape"}>
      {children}
    </div>
  );
};

interface ResponsiveGridProps {
  children: React.ReactNode;
  className?: string;
  minColumns?: number;
  maxColumns?: number;
}

/**
 * Responsive grid that adjusts columns based on orientation
 * More columns in landscape, fewer in portrait
 */
export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({ children, className = "", minColumns = 1, maxColumns = 3 }) => {
  const { isPortrait } = useDeviceOrientation();
  const { isMobile, isTablet, isDesktop } = useBreakpoint();

  const getGridColumns = () => {
    if (isMobile) {
      return isPortrait ? "grid-cols-1" : "grid-cols-2";
    }
    if (isTablet) {
      return isPortrait ? "grid-cols-2" : "grid-cols-3";
    }
    if (isDesktop) {
      return isPortrait ? `grid-cols-${Math.min(maxColumns, 3)}` : `grid-cols-${maxColumns}`;
    }
    return "grid-cols-1";
  };

  return <div className={`grid ${getGridColumns()} gap-4 sm:gap-6 ${className}`}>{children}</div>;
};

interface OrientationAwareContainerProps {
  children: React.ReactNode;
  portraitClassName?: string;
  landscapeClassName?: string;
  className?: string;
}

/**
 * Container that applies different styles based on orientation
 */
export const OrientationAwareContainer: React.FC<OrientationAwareContainerProps> = ({ children, portraitClassName = "", landscapeClassName = "", className = "" }) => {
  const { isPortrait } = useDeviceOrientation();

  return <div className={`${className} ${isPortrait ? portraitClassName : landscapeClassName}`}>{children}</div>;
};
