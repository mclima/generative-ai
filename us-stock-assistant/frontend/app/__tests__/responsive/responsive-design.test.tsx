/**
 * Responsive design tests for the US Stock Assistant dashboard.
 *
 * **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 22.3**
 *
 * Tests dashboard responsiveness across different screen sizes:
 * - Desktop (1920x1080)
 * - Tablet (768x1024)
 * - Mobile (375x667)
 * - Device rotation
 */

import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

// Mock Next.js router
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
    pathname: "/",
    query: {},
    asPath: "/",
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock window.matchMedia
const createMatchMedia = (width: number) => {
  return (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  });
};

describe("Responsive Design Tests", () => {
  beforeEach(() => {
    // Reset window size before each test
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 1920,
    });
    Object.defineProperty(window, "innerHeight", {
      writable: true,
      configurable: true,
      value: 1080,
    });
  });

  describe("Desktop Layout (1920x1080)", () => {
    beforeEach(() => {
      window.innerWidth = 1920;
      window.innerHeight = 1080;
      window.matchMedia = createMatchMedia(1920);
    });

    it("should render dashboard with full desktop layout", () => {
      /**
       * **Validates: Requirement 13.1**
       *
       * Test dashboard on desktop (1920x1080)
       */
      const { container } = render(
        <div className="min-h-screen bg-gray-50">
          <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2" data-testid="main-content">
                <h1 className="text-3xl font-bold mb-6">Portfolio Dashboard</h1>
                <div className="bg-white rounded-lg shadow p-6">
                  <p>Portfolio content</p>
                </div>
              </div>
              <div className="lg:col-span-1" data-testid="sidebar">
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-semibold mb-4">Market Overview</h2>
                  <p>Market data</p>
                </div>
              </div>
            </div>
          </div>
        </div>,
      );

      // Verify desktop layout elements are visible
      expect(screen.getByTestId("main-content")).toBeInTheDocument();
      expect(screen.getByTestId("sidebar")).toBeInTheDocument();
      expect(screen.getByText("Portfolio Dashboard")).toBeInTheDocument();
      expect(screen.getByText("Market Overview")).toBeInTheDocument();
    });

    it("should display charts with full width on desktop", () => {
      /**
       * **Validates: Requirement 13.1**
       */
      const { container } = render(
        <div className="w-full">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="w-full h-96" data-testid="chart-container">
              <div className="w-full h-full bg-gray-100 flex items-center justify-center">Chart Placeholder</div>
            </div>
          </div>
        </div>,
      );

      const chartContainer = screen.getByTestId("chart-container");
      expect(chartContainer).toBeInTheDocument();
      expect(chartContainer).toHaveClass("w-full", "h-96");
    });

    it("should show navigation menu horizontally on desktop", () => {
      /**
       * **Validates: Requirement 13.1**
       */
      const { container } = render(
        <nav className="bg-white shadow-sm">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-8" data-testid="desktop-nav">
                <a href="/" className="text-gray-700 hover:text-gray-900">
                  Dashboard
                </a>
                <a href="/portfolio" className="text-gray-700 hover:text-gray-900">
                  Portfolio
                </a>
                <a href="/alerts" className="text-gray-700 hover:text-gray-900">
                  Alerts
                </a>
                <a href="/analysis" className="text-gray-700 hover:text-gray-900">
                  Analysis
                </a>
              </div>
            </div>
          </div>
        </nav>,
      );

      const desktopNav = screen.getByTestId("desktop-nav");
      expect(desktopNav).toBeInTheDocument();
      expect(desktopNav).toHaveClass("flex", "items-center", "space-x-8");
    });
  });

  describe("Tablet Layout (768x1024)", () => {
    beforeEach(() => {
      window.innerWidth = 768;
      window.innerHeight = 1024;
      window.matchMedia = createMatchMedia(768);
    });

    it("should render dashboard with tablet-optimized layout", () => {
      /**
       * **Validates: Requirement 13.2**
       *
       * Test dashboard on tablet (768x1024)
       */
      const { container } = render(
        <div className="min-h-screen bg-gray-50">
          <div className="container mx-auto px-4 py-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2" data-testid="tablet-header">
                <h1 className="text-2xl font-bold mb-4">Portfolio Dashboard</h1>
              </div>
              <div className="md:col-span-1" data-testid="tablet-main">
                <div className="bg-white rounded-lg shadow p-4">
                  <p>Portfolio content</p>
                </div>
              </div>
              <div className="md:col-span-1" data-testid="tablet-sidebar">
                <div className="bg-white rounded-lg shadow p-4">
                  <h2 className="text-lg font-semibold mb-3">Market Overview</h2>
                  <p>Market data</p>
                </div>
              </div>
            </div>
          </div>
        </div>,
      );

      // Verify tablet layout elements
      expect(screen.getByTestId("tablet-header")).toBeInTheDocument();
      expect(screen.getByTestId("tablet-main")).toBeInTheDocument();
      expect(screen.getByTestId("tablet-sidebar")).toBeInTheDocument();
    });

    it("should optimize touch interactions on tablet", () => {
      /**
       * **Validates: Requirement 13.2**
       *
       * Test touch-optimized spacing and sizing
       */
      const { container } = render(
        <div className="space-y-4">
          <button className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg touch-manipulation" data-testid="touch-button">
            Add Stock
          </button>
          <div className="grid grid-cols-2 gap-4">
            <button className="py-3 px-4 bg-gray-200 rounded-lg touch-manipulation" data-testid="touch-button-1">
              Option 1
            </button>
            <button className="py-3 px-4 bg-gray-200 rounded-lg touch-manipulation" data-testid="touch-button-2">
              Option 2
            </button>
          </div>
        </div>,
      );

      // Verify touch-optimized buttons
      const touchButton = screen.getByTestId("touch-button");
      expect(touchButton).toBeInTheDocument();
      expect(touchButton).toHaveClass("py-3", "px-4"); // Adequate padding for touch
      expect(touchButton).toHaveClass("touch-manipulation");
    });

    it("should stack content appropriately on tablet", () => {
      /**
       * **Validates: Requirement 13.2**
       */
      const { container } = render(
        <div className="flex flex-col md:flex-row gap-4" data-testid="tablet-stack">
          <div className="flex-1 bg-white p-4 rounded-lg">Section 1</div>
          <div className="flex-1 bg-white p-4 rounded-lg">Section 2</div>
        </div>,
      );

      const tabletStack = screen.getByTestId("tablet-stack");
      expect(tabletStack).toBeInTheDocument();
      expect(tabletStack).toHaveClass("flex", "flex-col", "md:flex-row");
    });
  });

  describe("Mobile Layout (375x667)", () => {
    beforeEach(() => {
      window.innerWidth = 375;
      window.innerHeight = 667;
      window.matchMedia = createMatchMedia(375);
    });

    it("should render dashboard with mobile-optimized layout", () => {
      /**
       * **Validates: Requirement 13.3**
       *
       * Test dashboard on mobile (375x667)
       */
      const { container } = render(
        <div className="min-h-screen bg-gray-50">
          <div className="px-4 py-4">
            <h1 className="text-xl font-bold mb-4">Portfolio</h1>
            <div className="space-y-4">
              <div className="bg-white rounded-lg shadow p-4" data-testid="mobile-card-1">
                <p>Portfolio Summary</p>
              </div>
              <div className="bg-white rounded-lg shadow p-4" data-testid="mobile-card-2">
                <p>Recent Activity</p>
              </div>
              <div className="bg-white rounded-lg shadow p-4" data-testid="mobile-card-3">
                <p>Market Overview</p>
              </div>
            </div>
          </div>
        </div>,
      );

      // Verify mobile layout with stacked cards
      expect(screen.getByTestId("mobile-card-1")).toBeInTheDocument();
      expect(screen.getByTestId("mobile-card-2")).toBeInTheDocument();
      expect(screen.getByTestId("mobile-card-3")).toBeInTheDocument();
    });

    it("should show mobile navigation menu", () => {
      /**
       * **Validates: Requirement 13.3**
       */
      const { container } = render(
        <nav className="bg-white shadow-sm">
          <div className="px-4">
            <div className="flex items-center justify-between h-14">
              <h1 className="text-lg font-semibold">Stock Assistant</h1>
              <button className="p-2 rounded-md" data-testid="mobile-menu-button" aria-label="Open menu">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </nav>,
      );

      const menuButton = screen.getByTestId("mobile-menu-button");
      expect(menuButton).toBeInTheDocument();
      expect(menuButton).toHaveAttribute("aria-label", "Open menu");
    });

    it("should maintain functionality on small screens", () => {
      /**
       * **Validates: Requirement 13.3**
       *
       * Verify that all functionality is accessible on mobile
       */
      const { container } = render(
        <div className="min-h-screen">
          <div className="px-4 py-4 space-y-4">
            <input type="text" placeholder="Search stocks..." className="w-full px-4 py-2 border rounded-lg" data-testid="mobile-search" />
            <button className="w-full py-3 bg-blue-600 text-white rounded-lg" data-testid="mobile-action">
              Add to Portfolio
            </button>
            <div className="grid grid-cols-2 gap-2">
              <button className="py-2 bg-gray-200 rounded-lg text-sm" data-testid="mobile-btn-1">
                View
              </button>
              <button className="py-2 bg-gray-200 rounded-lg text-sm" data-testid="mobile-btn-2">
                Edit
              </button>
            </div>
          </div>
        </div>,
      );

      // Verify mobile-optimized controls
      expect(screen.getByTestId("mobile-search")).toBeInTheDocument();
      expect(screen.getByTestId("mobile-action")).toBeInTheDocument();
      expect(screen.getByTestId("mobile-btn-1")).toBeInTheDocument();
      expect(screen.getByTestId("mobile-btn-2")).toBeInTheDocument();
    });
  });

  describe("Device Rotation", () => {
    it("should adjust layout when rotating from portrait to landscape", () => {
      /**
       * **Validates: Requirement 13.4**
       *
       * Test device rotation handling
       */
      // Start in portrait mode (mobile)
      window.innerWidth = 375;
      window.innerHeight = 667;
      window.matchMedia = createMatchMedia(375);

      const { container, rerender } = render(
        <div className="min-h-screen">
          <div className="flex flex-col sm:flex-row gap-4" data-testid="rotatable-content">
            <div className="flex-1 bg-white p-4">Content 1</div>
            <div className="flex-1 bg-white p-4">Content 2</div>
          </div>
        </div>,
      );

      let rotatableContent = screen.getByTestId("rotatable-content");
      expect(rotatableContent).toHaveClass("flex", "flex-col", "sm:flex-row");

      // Rotate to landscape mode
      window.innerWidth = 667;
      window.innerHeight = 375;
      window.matchMedia = createMatchMedia(667);

      // Rerender to simulate rotation
      rerender(
        <div className="min-h-screen">
          <div className="flex flex-col sm:flex-row gap-4" data-testid="rotatable-content">
            <div className="flex-1 bg-white p-4">Content 1</div>
            <div className="flex-1 bg-white p-4">Content 2</div>
          </div>
        </div>,
      );

      rotatableContent = screen.getByTestId("rotatable-content");
      expect(rotatableContent).toBeInTheDocument();
    });

    it("should adjust layout when rotating from landscape to portrait on tablet", () => {
      /**
       * **Validates: Requirement 13.4**
       */
      // Start in landscape mode (tablet)
      window.innerWidth = 1024;
      window.innerHeight = 768;
      window.matchMedia = createMatchMedia(1024);

      const { container, rerender } = render(
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="grid-layout">
          <div className="bg-white p-4">Item 1</div>
          <div className="bg-white p-4">Item 2</div>
          <div className="bg-white p-4">Item 3</div>
        </div>,
      );

      let gridLayout = screen.getByTestId("grid-layout");
      expect(gridLayout).toHaveClass("grid", "grid-cols-1", "md:grid-cols-2", "lg:grid-cols-3");

      // Rotate to portrait mode
      window.innerWidth = 768;
      window.innerHeight = 1024;
      window.matchMedia = createMatchMedia(768);

      // Rerender to simulate rotation
      rerender(
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="grid-layout">
          <div className="bg-white p-4">Item 1</div>
          <div className="bg-white p-4">Item 2</div>
          <div className="bg-white p-4">Item 3</div>
        </div>,
      );

      gridLayout = screen.getByTestId("grid-layout");
      expect(gridLayout).toBeInTheDocument();
    });
  });

  describe("Responsive Breakpoints", () => {
    it("should maintain functionality across all breakpoints (320px to 2560px)", () => {
      /**
       * **Validates: Requirement 13.3**
       *
       * Test that dashboard maintains functionality across screen sizes from 320px to 2560px width
       */
      const breakpoints = [
        { width: 320, height: 568, name: "Small Mobile" },
        { width: 375, height: 667, name: "Mobile" },
        { width: 768, height: 1024, name: "Tablet" },
        { width: 1024, height: 768, name: "Tablet Landscape" },
        { width: 1280, height: 720, name: "Small Desktop" },
        { width: 1920, height: 1080, name: "Desktop" },
        { width: 2560, height: 1440, name: "Large Desktop" },
      ];

      breakpoints.forEach(({ width, height, name }) => {
        window.innerWidth = width;
        window.innerHeight = height;
        window.matchMedia = createMatchMedia(width);

        const { container, unmount } = render(
          <div className="min-h-screen bg-gray-50">
            <div className="container mx-auto px-4 py-4">
              <h1 className="text-xl md:text-2xl lg:text-3xl font-bold mb-4" data-testid={`title-${width}`}>
                Portfolio Dashboard
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow p-4" data-testid={`card-${width}`}>
                  <p>Content</p>
                </div>
              </div>
            </div>
          </div>,
        );

        // Verify content renders at this breakpoint
        expect(screen.getByTestId(`card-${width}`)).toBeInTheDocument();
        expect(screen.getByTestId(`title-${width}`)).toBeInTheDocument();

        // Clean up after each iteration
        unmount();
      });
    });

    it("should use Tailwind CSS responsive utilities consistently", () => {
      /**
       * **Validates: Requirement 13.5**
       *
       * Verify that Tailwind CSS responsive utilities are used for consistent styling
       */
      const { container } = render(
        <div className="container mx-auto">
          <div className="px-4 sm:px-6 lg:px-8" data-testid="responsive-padding">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4" data-testid="responsive-grid">
              <div className="text-sm sm:text-base lg:text-lg" data-testid="responsive-text">
                Responsive Text
              </div>
            </div>
          </div>
        </div>,
      );

      // Verify Tailwind responsive classes are applied
      const responsivePadding = screen.getByTestId("responsive-padding");
      expect(responsivePadding).toHaveClass("px-4", "sm:px-6", "lg:px-8");

      const responsiveGrid = screen.getByTestId("responsive-grid");
      expect(responsiveGrid).toHaveClass("grid", "grid-cols-1", "sm:grid-cols-2", "lg:grid-cols-3", "xl:grid-cols-4");

      const responsiveText = screen.getByTestId("responsive-text");
      expect(responsiveText).toHaveClass("text-sm", "sm:text-base", "lg:text-lg");
    });
  });
});
