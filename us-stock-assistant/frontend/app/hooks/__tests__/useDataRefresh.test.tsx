import { renderHook, act } from "@testing-library/react";
import { useDataRefresh } from "../useDataRefresh";
import { usePreferences } from "@/app/contexts/PreferencesContext";
import { ReactNode } from "react";

// Mock the PreferencesContext
jest.mock("@/app/contexts/PreferencesContext");

const mockUsePreferences = usePreferences as jest.MockedFunction<typeof usePreferences>;

describe("useDataRefresh", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it("should call callback at specified refresh interval", () => {
    const callback = jest.fn();
    const mockPreferences = {
      default_chart_type: "line" as const,
      default_time_range: "1M" as const,
      preferred_news_sources: [],
      notification_settings: {
        in_app: true,
        email: false,
        push: false,
        alert_types: {
          price_alerts: true,
          news_updates: true,
          portfolio_changes: true,
        },
      },
      refresh_interval: 60,
    };

    mockUsePreferences.mockReturnValue({
      preferences: mockPreferences,
      loading: false,
      error: null,
      refreshPreferences: jest.fn(),
    });

    renderHook(() => useDataRefresh(callback, true));

    expect(callback).not.toHaveBeenCalled();

    // Fast-forward 60 seconds
    act(() => {
      jest.advanceTimersByTime(60000);
    });

    expect(callback).toHaveBeenCalledTimes(1);

    // Fast-forward another 60 seconds
    act(() => {
      jest.advanceTimersByTime(60000);
    });

    expect(callback).toHaveBeenCalledTimes(2);
  });

  it("should not call callback when disabled", () => {
    const callback = jest.fn();
    const mockPreferences = {
      default_chart_type: "line" as const,
      default_time_range: "1M" as const,
      preferred_news_sources: [],
      notification_settings: {
        in_app: true,
        email: false,
        push: false,
        alert_types: {
          price_alerts: true,
          news_updates: true,
          portfolio_changes: true,
        },
      },
      refresh_interval: 60,
    };

    mockUsePreferences.mockReturnValue({
      preferences: mockPreferences,
      loading: false,
      error: null,
      refreshPreferences: jest.fn(),
    });

    renderHook(() => useDataRefresh(callback, false));

    act(() => {
      jest.advanceTimersByTime(120000);
    });

    expect(callback).not.toHaveBeenCalled();
  });

  it("should not call callback when preferences are null", () => {
    const callback = jest.fn();

    mockUsePreferences.mockReturnValue({
      preferences: null,
      loading: true,
      error: null,
      refreshPreferences: jest.fn(),
    });

    renderHook(() => useDataRefresh(callback, true));

    act(() => {
      jest.advanceTimersByTime(120000);
    });

    expect(callback).not.toHaveBeenCalled();
  });

  it("should update interval when preferences change", () => {
    const callback = jest.fn();
    const mockPreferences1 = {
      default_chart_type: "line" as const,
      default_time_range: "1M" as const,
      preferred_news_sources: [],
      notification_settings: {
        in_app: true,
        email: false,
        push: false,
        alert_types: {
          price_alerts: true,
          news_updates: true,
          portfolio_changes: true,
        },
      },
      refresh_interval: 60,
    };

    mockUsePreferences.mockReturnValue({
      preferences: mockPreferences1,
      loading: false,
      error: null,
      refreshPreferences: jest.fn(),
    });

    const { rerender } = renderHook(() => useDataRefresh(callback, true));

    // Fast-forward 60 seconds
    act(() => {
      jest.advanceTimersByTime(60000);
    });

    expect(callback).toHaveBeenCalledTimes(1);

    // Update preferences with new refresh interval
    const mockPreferences2 = {
      ...mockPreferences1,
      refresh_interval: 30,
    };

    mockUsePreferences.mockReturnValue({
      preferences: mockPreferences2,
      loading: false,
      error: null,
      refreshPreferences: jest.fn(),
    });

    rerender();

    // Fast-forward 30 seconds (new interval)
    act(() => {
      jest.advanceTimersByTime(30000);
    });

    expect(callback).toHaveBeenCalledTimes(2);
  });

  it("should use updated callback function", () => {
    const callback1 = jest.fn();
    const callback2 = jest.fn();
    const mockPreferences = {
      default_chart_type: "line" as const,
      default_time_range: "1M" as const,
      preferred_news_sources: [],
      notification_settings: {
        in_app: true,
        email: false,
        push: false,
        alert_types: {
          price_alerts: true,
          news_updates: true,
          portfolio_changes: true,
        },
      },
      refresh_interval: 60,
    };

    mockUsePreferences.mockReturnValue({
      preferences: mockPreferences,
      loading: false,
      error: null,
      refreshPreferences: jest.fn(),
    });

    const { rerender } = renderHook(({ cb }) => useDataRefresh(cb, true), { initialProps: { cb: callback1 } });

    act(() => {
      jest.advanceTimersByTime(60000);
    });

    expect(callback1).toHaveBeenCalledTimes(1);
    expect(callback2).not.toHaveBeenCalled();

    // Update callback
    rerender({ cb: callback2 });

    act(() => {
      jest.advanceTimersByTime(60000);
    });

    expect(callback1).toHaveBeenCalledTimes(1);
    expect(callback2).toHaveBeenCalledTimes(1);
  });

  it("should cleanup interval on unmount", () => {
    const callback = jest.fn();
    const mockPreferences = {
      default_chart_type: "line" as const,
      default_time_range: "1M" as const,
      preferred_news_sources: [],
      notification_settings: {
        in_app: true,
        email: false,
        push: false,
        alert_types: {
          price_alerts: true,
          news_updates: true,
          portfolio_changes: true,
        },
      },
      refresh_interval: 60,
    };

    mockUsePreferences.mockReturnValue({
      preferences: mockPreferences,
      loading: false,
      error: null,
      refreshPreferences: jest.fn(),
    });

    const { unmount } = renderHook(() => useDataRefresh(callback, true));

    unmount();

    act(() => {
      jest.advanceTimersByTime(120000);
    });

    expect(callback).not.toHaveBeenCalled();
  });

  it("should handle different refresh intervals correctly", () => {
    const callback = jest.fn();

    // Test with 15 seconds
    mockUsePreferences.mockReturnValue({
      preferences: {
        default_chart_type: "line" as const,
        default_time_range: "1M" as const,
        preferred_news_sources: [],
        notification_settings: {
          in_app: true,
          email: false,
          push: false,
          alert_types: {
            price_alerts: true,
            news_updates: true,
            portfolio_changes: true,
          },
        },
        refresh_interval: 15,
      },
      loading: false,
      error: null,
      refreshPreferences: jest.fn(),
    });

    const { unmount } = renderHook(() => useDataRefresh(callback, true));

    act(() => {
      jest.advanceTimersByTime(15000);
    });

    expect(callback).toHaveBeenCalledTimes(1);

    unmount();
  });
});
