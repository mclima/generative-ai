import { renderHook, act } from "@testing-library/react";
import { useDeviceOrientation, useBreakpoint } from "../useDeviceOrientation";

describe("useDeviceOrientation", () => {
  beforeEach(() => {
    // Reset window dimensions
    global.innerWidth = 1024;
    global.innerHeight = 768;
  });

  it("should detect portrait orientation", () => {
    global.innerWidth = 375;
    global.innerHeight = 667;

    const { result } = renderHook(() => useDeviceOrientation());

    expect(result.current.orientation).toBe("portrait");
    expect(result.current.isPortrait).toBe(true);
    expect(result.current.isLandscape).toBe(false);
  });

  it("should detect landscape orientation", () => {
    global.innerWidth = 667;
    global.innerHeight = 375;

    const { result } = renderHook(() => useDeviceOrientation());

    expect(result.current.orientation).toBe("landscape");
    expect(result.current.isPortrait).toBe(false);
    expect(result.current.isLandscape).toBe(true);
  });

  it("should update orientation on window resize", () => {
    global.innerWidth = 375;
    global.innerHeight = 667;

    const { result } = renderHook(() => useDeviceOrientation());

    expect(result.current.orientation).toBe("portrait");

    // Simulate device rotation
    act(() => {
      global.innerWidth = 667;
      global.innerHeight = 375;
      window.dispatchEvent(new Event("resize"));
    });

    expect(result.current.orientation).toBe("landscape");
  });

  it("should update on orientationchange event", () => {
    global.innerWidth = 375;
    global.innerHeight = 667;

    const { result } = renderHook(() => useDeviceOrientation());

    expect(result.current.orientation).toBe("portrait");

    // Simulate orientation change
    act(() => {
      global.innerWidth = 667;
      global.innerHeight = 375;
      window.dispatchEvent(new Event("orientationchange"));
    });

    expect(result.current.orientation).toBe("landscape");
  });

  it("should handle screen orientation API if available", () => {
    const mockScreenOrientation = {
      angle: 90,
      type: "landscape-primary",
    };

    Object.defineProperty(window, "screen", {
      writable: true,
      value: {
        orientation: mockScreenOrientation,
      },
    });

    global.innerWidth = 667;
    global.innerHeight = 375;

    const { result } = renderHook(() => useDeviceOrientation());

    expect(result.current.angle).toBe(90);
  });
});

describe("useBreakpoint", () => {
  beforeEach(() => {
    global.innerWidth = 1024;
  });

  it("should detect xs breakpoint (< 640px)", () => {
    global.innerWidth = 375;

    const { result } = renderHook(() => useBreakpoint());

    expect(result.current.breakpoint).toBe("xs");
    expect(result.current.isMobile).toBe(true);
    expect(result.current.isTablet).toBe(false);
    expect(result.current.isDesktop).toBe(false);
  });

  it("should detect sm breakpoint (640px - 768px)", () => {
    global.innerWidth = 640;

    const { result } = renderHook(() => useBreakpoint());

    expect(result.current.breakpoint).toBe("sm");
    expect(result.current.isMobile).toBe(true);
  });

  it("should detect md breakpoint (768px - 1024px)", () => {
    global.innerWidth = 768;

    const { result } = renderHook(() => useBreakpoint());

    expect(result.current.breakpoint).toBe("md");
    expect(result.current.isMobile).toBe(false);
    expect(result.current.isTablet).toBe(true);
    expect(result.current.isDesktop).toBe(false);
  });

  it("should detect lg breakpoint (1024px - 1280px)", () => {
    global.innerWidth = 1024;

    const { result } = renderHook(() => useBreakpoint());

    expect(result.current.breakpoint).toBe("lg");
    expect(result.current.isMobile).toBe(false);
    expect(result.current.isTablet).toBe(false);
    expect(result.current.isDesktop).toBe(true);
  });

  it("should detect xl breakpoint (1280px - 1536px)", () => {
    global.innerWidth = 1280;

    const { result } = renderHook(() => useBreakpoint());

    expect(result.current.breakpoint).toBe("xl");
    expect(result.current.isDesktop).toBe(true);
  });

  it("should detect 2xl breakpoint (>= 1536px)", () => {
    global.innerWidth = 1920;

    const { result } = renderHook(() => useBreakpoint());

    expect(result.current.breakpoint).toBe("2xl");
    expect(result.current.isDesktop).toBe(true);
  });

  it("should update breakpoint on window resize", () => {
    global.innerWidth = 375;

    const { result } = renderHook(() => useBreakpoint());

    expect(result.current.breakpoint).toBe("xs");

    // Resize to desktop
    act(() => {
      global.innerWidth = 1280;
      window.dispatchEvent(new Event("resize"));
    });

    expect(result.current.breakpoint).toBe("xl");
    expect(result.current.isDesktop).toBe(true);
  });
});
