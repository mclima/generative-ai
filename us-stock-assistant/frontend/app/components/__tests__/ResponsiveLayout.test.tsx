import { render, screen, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ResponsiveLayout, ResponsiveGrid, OrientationAwareContainer } from "../ResponsiveLayout";

// Mock the hooks
jest.mock("@/app/hooks/useDeviceOrientation", () => ({
  useDeviceOrientation: jest.fn(() => ({
    orientation: "portrait",
    angle: 0,
    isPortrait: true,
    isLandscape: false,
  })),
  useBreakpoint: jest.fn(() => ({
    breakpoint: "md",
    isMobile: false,
    isTablet: true,
    isDesktop: false,
  })),
}));

import { useDeviceOrientation, useBreakpoint } from "@/app/hooks/useDeviceOrientation";

describe("ResponsiveLayout", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render children", () => {
    render(
      <ResponsiveLayout>
        <div>Test Content</div>
      </ResponsiveLayout>,
    );

    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  it("should apply mobile portrait padding", () => {
    (useBreakpoint as jest.Mock).mockReturnValue({
      breakpoint: "xs",
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "portrait",
      isPortrait: true,
      isLandscape: false,
    });

    const { container } = render(
      <ResponsiveLayout>
        <div>Test</div>
      </ResponsiveLayout>,
    );

    const layout = container.firstChild as HTMLElement;
    expect(layout).toHaveClass("p-4");
  });

  it("should apply mobile landscape padding", () => {
    (useBreakpoint as jest.Mock).mockReturnValue({
      breakpoint: "xs",
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "landscape",
      isPortrait: false,
      isLandscape: true,
    });

    const { container } = render(
      <ResponsiveLayout>
        <div>Test</div>
      </ResponsiveLayout>,
    );

    const layout = container.firstChild as HTMLElement;
    expect(layout).toHaveClass("p-3");
  });

  it("should apply tablet portrait padding", () => {
    (useBreakpoint as jest.Mock).mockReturnValue({
      breakpoint: "md",
      isMobile: false,
      isTablet: true,
      isDesktop: false,
    });
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "portrait",
      isPortrait: true,
      isLandscape: false,
    });

    const { container } = render(
      <ResponsiveLayout>
        <div>Test</div>
      </ResponsiveLayout>,
    );

    const layout = container.firstChild as HTMLElement;
    expect(layout).toHaveClass("p-6");
  });

  it("should apply desktop padding", () => {
    (useBreakpoint as jest.Mock).mockReturnValue({
      breakpoint: "lg",
      isMobile: false,
      isTablet: false,
      isDesktop: true,
    });

    const { container } = render(
      <ResponsiveLayout>
        <div>Test</div>
      </ResponsiveLayout>,
    );

    const layout = container.firstChild as HTMLElement;
    expect(layout).toHaveClass("p-8");
  });

  it("should set data-orientation attribute", () => {
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "landscape",
      isPortrait: false,
      isLandscape: true,
    });

    const { container } = render(
      <ResponsiveLayout>
        <div>Test</div>
      </ResponsiveLayout>,
    );

    const layout = container.firstChild as HTMLElement;
    expect(layout).toHaveAttribute("data-orientation", "landscape");
  });
});

describe("ResponsiveGrid", () => {
  it("should render children in a grid", () => {
    render(
      <ResponsiveGrid>
        <div>Item 1</div>
        <div>Item 2</div>
      </ResponsiveGrid>,
    );

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 2")).toBeInTheDocument();
  });

  it("should apply 1 column on mobile portrait", () => {
    (useBreakpoint as jest.Mock).mockReturnValue({
      breakpoint: "xs",
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "portrait",
      isPortrait: true,
      isLandscape: false,
    });

    const { container } = render(
      <ResponsiveGrid>
        <div>Item</div>
      </ResponsiveGrid>,
    );

    const grid = container.firstChild as HTMLElement;
    expect(grid).toHaveClass("grid-cols-1");
  });

  it("should apply 2 columns on mobile landscape", () => {
    (useBreakpoint as jest.Mock).mockReturnValue({
      breakpoint: "xs",
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "landscape",
      isPortrait: false,
      isLandscape: true,
    });

    const { container } = render(
      <ResponsiveGrid>
        <div>Item</div>
      </ResponsiveGrid>,
    );

    const grid = container.firstChild as HTMLElement;
    expect(grid).toHaveClass("grid-cols-2");
  });

  it("should apply 2 columns on tablet portrait", () => {
    (useBreakpoint as jest.Mock).mockReturnValue({
      breakpoint: "md",
      isMobile: false,
      isTablet: true,
      isDesktop: false,
    });
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "portrait",
      isPortrait: true,
      isLandscape: false,
    });

    const { container } = render(
      <ResponsiveGrid>
        <div>Item</div>
      </ResponsiveGrid>,
    );

    const grid = container.firstChild as HTMLElement;
    expect(grid).toHaveClass("grid-cols-2");
  });

  it("should apply 3 columns on tablet landscape", () => {
    (useBreakpoint as jest.Mock).mockReturnValue({
      breakpoint: "md",
      isMobile: false,
      isTablet: true,
      isDesktop: false,
    });
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "landscape",
      isPortrait: false,
      isLandscape: true,
    });

    const { container } = render(
      <ResponsiveGrid>
        <div>Item</div>
      </ResponsiveGrid>,
    );

    const grid = container.firstChild as HTMLElement;
    expect(grid).toHaveClass("grid-cols-3");
  });

  it("should have responsive gap classes", () => {
    const { container } = render(
      <ResponsiveGrid>
        <div>Item</div>
      </ResponsiveGrid>,
    );

    const grid = container.firstChild as HTMLElement;
    expect(grid).toHaveClass("gap-4", "sm:gap-6");
  });
});

describe("OrientationAwareContainer", () => {
  it("should apply portrait className when in portrait mode", () => {
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "portrait",
      isPortrait: true,
      isLandscape: false,
    });

    const { container } = render(
      <OrientationAwareContainer portraitClassName="portrait-class" landscapeClassName="landscape-class">
        <div>Content</div>
      </OrientationAwareContainer>,
    );

    const element = container.firstChild as HTMLElement;
    expect(element).toHaveClass("portrait-class");
    expect(element).not.toHaveClass("landscape-class");
  });

  it("should apply landscape className when in landscape mode", () => {
    (useDeviceOrientation as jest.Mock).mockReturnValue({
      orientation: "landscape",
      isPortrait: false,
      isLandscape: true,
    });

    const { container } = render(
      <OrientationAwareContainer portraitClassName="portrait-class" landscapeClassName="landscape-class">
        <div>Content</div>
      </OrientationAwareContainer>,
    );

    const element = container.firstChild as HTMLElement;
    expect(element).toHaveClass("landscape-class");
    expect(element).not.toHaveClass("portrait-class");
  });

  it("should apply base className in both orientations", () => {
    const { container } = render(
      <OrientationAwareContainer className="base-class">
        <div>Content</div>
      </OrientationAwareContainer>,
    );

    const element = container.firstChild as HTMLElement;
    expect(element).toHaveClass("base-class");
  });
});
