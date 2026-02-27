import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import MarketOverview from "../MarketOverview";
import { marketApi } from "@/app/lib/api/market";
import type { MarketOverview as MarketOverviewType } from "@/app/types/market";

// Mock the market API
jest.mock("@/app/lib/api/market", () => ({
  marketApi: {
    getMarketOverview: jest.fn(),
  },
}));

// Mock child components
jest.mock("../MarketIndices", () => {
  return function MockMarketIndices({ indices }: any) {
    return <div data-testid="market-indices">Market Indices: {indices.length}</div>;
  };
});

jest.mock("../MarketHeadlines", () => {
  return function MockMarketHeadlines({ headlines }: any) {
    return <div data-testid="market-headlines">Headlines: {headlines.length}</div>;
  };
});

jest.mock("../MarketSentiment", () => {
  return function MockMarketSentiment({ sentiment }: any) {
    return <div data-testid="market-sentiment">Sentiment: {sentiment.label}</div>;
  };
});

jest.mock("../TrendingTickers", () => {
  return function MockTrendingTickers({ tickers }: any) {
    return <div data-testid="trending-tickers">Trending: {tickers.length}</div>;
  };
});

jest.mock("../SectorHeatmap", () => {
  return function MockSectorHeatmap({ sectors }: any) {
    return <div data-testid="sector-heatmap">Sectors: {sectors.length}</div>;
  };
});

const mockMarketData: MarketOverviewType = {
  headlines: [
    {
      id: "1",
      headline: "Market reaches new highs",
      source: "CNBC",
      url: "https://example.com/1",
      published_at: new Date().toISOString(),
      summary: "Markets continue upward trend",
      sentiment: { label: "positive", score: 0.8, confidence: 0.9 },
    },
  ],
  sentiment: {
    label: "positive",
    score: 0.65,
    confidence: 0.85,
  },
  trending_tickers: [
    {
      ticker: "AAPL",
      company_name: "Apple Inc.",
      price: 150.25,
      change_percent: 2.5,
      volume: 50000000,
      news_count: 10,
      reason: "Strong earnings report",
    },
  ],
  indices: [
    {
      name: "S&P 500",
      symbol: "^GSPC",
      value: 4500.0,
      change: 25.5,
      change_percent: 0.57,
    },
    {
      name: "NASDAQ",
      symbol: "^IXIC",
      value: 14000.0,
      change: 100.0,
      change_percent: 0.72,
    },
    {
      name: "DOW",
      symbol: "^DJI",
      value: 35000.0,
      change: 150.0,
      change_percent: 0.43,
    },
  ],
  sector_heatmap: [
    {
      sector: "Technology",
      change_percent: 1.5,
      top_performers: ["AAPL", "MSFT"],
      bottom_performers: ["IBM"],
    },
  ],
  last_updated: new Date().toISOString(),
};

describe("MarketOverview Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe("Component Rendering", () => {
    it("renders all market overview sections", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByTestId("market-indices")).toBeInTheDocument();
        expect(screen.getByTestId("market-sentiment")).toBeInTheDocument();
        expect(screen.getByTestId("trending-tickers")).toBeInTheDocument();
        expect(screen.getByTestId("market-headlines")).toBeInTheDocument();
      });
    });

    it("fetches market overview data on mount", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(marketApi.getMarketOverview).toHaveBeenCalledTimes(1);
      });
    });

    it("displays last updated timestamp", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
      });
    });
  });

  describe("Data Rendering", () => {
    it("passes correct data to MarketIndices component", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByText("Market Indices: 3")).toBeInTheDocument();
      });
    });

    it("passes correct data to MarketSentiment component", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByText("Sentiment: positive")).toBeInTheDocument();
      });
    });

    it("passes correct data to TrendingTickers component", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByText("Trending: 1")).toBeInTheDocument();
      });
    });

    it("passes correct data to MarketHeadlines component", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByText("Headlines: 1")).toBeInTheDocument();
      });
    });
  });

  describe("Conditional Sector Heatmap Display", () => {
    it("displays sector heatmap when data is available", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByTestId("sector-heatmap")).toBeInTheDocument();
        expect(screen.getByText("Sectors: 1")).toBeInTheDocument();
      });
    });

    it("does not display sector heatmap when data is undefined", async () => {
      const dataWithoutHeatmap = {
        ...mockMarketData,
        sector_heatmap: undefined,
      };
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(dataWithoutHeatmap);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByTestId("market-indices")).toBeInTheDocument();
      });

      expect(screen.queryByTestId("sector-heatmap")).not.toBeInTheDocument();
    });

    it("does not display sector heatmap when data is empty array", async () => {
      const dataWithEmptyHeatmap = {
        ...mockMarketData,
        sector_heatmap: [],
      };
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(dataWithEmptyHeatmap);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByTestId("market-indices")).toBeInTheDocument();
      });

      expect(screen.queryByTestId("sector-heatmap")).not.toBeInTheDocument();
    });
  });

  describe("Loading States", () => {
    it("displays loading spinner while fetching data", async () => {
      let resolveData: (value: MarketOverviewType) => void;
      const dataPromise = new Promise<MarketOverviewType>((resolve) => {
        resolveData = resolve;
      });
      (marketApi.getMarketOverview as jest.Mock).mockReturnValue(dataPromise);

      render(<MarketOverview />);

      const spinner = document.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();

      resolveData!(mockMarketData);
    });

    it("hides loading spinner after data loads", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByTestId("market-indices")).toBeInTheDocument();
      });

      const spinner = document.querySelector(".animate-spin");
      expect(spinner).not.toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("displays error message when API call fails", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByText("Failed to load market overview. Please try again.")).toBeInTheDocument();
      });
    });

    it("shows retry button on error", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByText("Retry")).toBeInTheDocument();
      });
    });

    it("retries loading data when retry button is clicked", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockRejectedValueOnce(new Error("API Error")).mockResolvedValueOnce(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(screen.getByText("Retry")).toBeInTheDocument();
      });

      const retryButton = screen.getByText("Retry");
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByTestId("market-indices")).toBeInTheDocument();
      });

      expect(marketApi.getMarketOverview).toHaveBeenCalledTimes(2);
    });
  });

  describe("Auto-refresh", () => {
    it("refreshes data every 15 minutes", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      render(<MarketOverview />);

      await waitFor(() => {
        expect(marketApi.getMarketOverview).toHaveBeenCalledTimes(1);
      });

      // Fast-forward 15 minutes
      jest.advanceTimersByTime(15 * 60 * 1000);

      await waitFor(() => {
        expect(marketApi.getMarketOverview).toHaveBeenCalledTimes(2);
      });
    });

    it("cleans up interval on unmount", async () => {
      (marketApi.getMarketOverview as jest.Mock).mockResolvedValue(mockMarketData);

      const { unmount } = render(<MarketOverview />);

      await waitFor(() => {
        expect(marketApi.getMarketOverview).toHaveBeenCalledTimes(1);
      });

      unmount();

      // Fast-forward 15 minutes after unmount
      jest.advanceTimersByTime(15 * 60 * 1000);

      // Should still be 1 call (no additional calls after unmount)
      expect(marketApi.getMarketOverview).toHaveBeenCalledTimes(1);
    });
  });
});
