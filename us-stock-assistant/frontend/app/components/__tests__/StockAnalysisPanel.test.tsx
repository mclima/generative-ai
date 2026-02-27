import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import StockAnalysisPanel from "../StockAnalysisPanel";
import { analysisApi } from "@/app/lib/api/analysis";
import type { StockAnalysis } from "@/app/types/analysis";

// Mock the analysis API
jest.mock("@/app/lib/api/analysis", () => ({
  analysisApi: {
    analyzeStock: jest.fn(),
  },
}));

const mockAnalysis: StockAnalysis = {
  ticker: "AAPL",
  summary: "Apple shows strong fundamentals with positive market sentiment and bullish price trends.",
  price_analysis: {
    trend: "bullish",
    support: 150.25,
    resistance: 180.75,
    volatility: "medium",
  },
  sentiment_analysis: {
    overall: "positive",
    score: 0.75,
    news_count: 25,
  },
  recommendations: ["Consider accumulating on dips near support level", "Monitor resistance level for potential breakout", "Strong fundamentals support long-term holding"],
  risks: ["Market volatility may impact short-term performance", "Regulatory concerns in key markets", "Supply chain disruptions remain a concern"],
  generated_at: new Date().toISOString(),
};

describe("StockAnalysisPanel Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Component Rendering", () => {
    it("renders the component with title and analyze button", () => {
      render(<StockAnalysisPanel ticker="AAPL" />);

      expect(screen.getByText("AI Analysis")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /analyze/i })).toBeInTheDocument();
    });

    it("displays empty state initially", () => {
      render(<StockAnalysisPanel ticker="AAPL" />);

      expect(screen.getByText(/Click "Analyze" to get AI-powered insights/i)).toBeInTheDocument();
    });
  });

  describe("Analysis Triggering", () => {
    it("calls API when analyze button is clicked", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(analysisApi.analyzeStock).toHaveBeenCalledWith("AAPL");
      });
    });

    it("disables button during analysis", async () => {
      let resolveAnalysis: (value: StockAnalysis) => void;
      const analysisPromise = new Promise<StockAnalysis>((resolve) => {
        resolveAnalysis = resolve;
      });
      (analysisApi.analyzeStock as jest.Mock).mockReturnValue(analysisPromise);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(analyzeButton).toBeDisabled();
        expect(screen.getByText("Analyzing...")).toBeInTheDocument();
      });

      resolveAnalysis!(mockAnalysis);
    });
  });

  describe("Loading States", () => {
    it("displays loading state during analysis", async () => {
      let resolveAnalysis: (value: StockAnalysis) => void;
      const analysisPromise = new Promise<StockAnalysis>((resolve) => {
        resolveAnalysis = resolve;
      });
      (analysisApi.analyzeStock as jest.Mock).mockReturnValue(analysisPromise);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const loadingElements = document.querySelectorAll(".animate-pulse");
        expect(loadingElements.length).toBeGreaterThan(0);
      });

      resolveAnalysis!(mockAnalysis);
    });

    it("hides loading state after analysis completes", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(mockAnalysis.summary)).toBeInTheDocument();
      });

      const loadingElements = document.querySelectorAll(".animate-pulse");
      expect(loadingElements.length).toBe(0);
    });
  });

  describe("Analysis Display", () => {
    beforeEach(async () => {
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(mockAnalysis.summary)).toBeInTheDocument();
      });
    });

    it("displays summary section", () => {
      expect(screen.getByText("Summary")).toBeInTheDocument();
      expect(screen.getByText(mockAnalysis.summary)).toBeInTheDocument();
    });

    it("displays price analysis section", () => {
      expect(screen.getByText("Price Trends")).toBeInTheDocument();
      expect(screen.getByText("bullish")).toBeInTheDocument();
      expect(screen.getByText("medium")).toBeInTheDocument();
      expect(screen.getByText("$150.25")).toBeInTheDocument();
      expect(screen.getByText("$180.75")).toBeInTheDocument();
    });

    it("displays sentiment analysis section", () => {
      expect(screen.getByText("Market Sentiment")).toBeInTheDocument();
      expect(screen.getByText("positive")).toBeInTheDocument();
      expect(screen.getByText("0.75")).toBeInTheDocument();
      expect(screen.getByText("25 news articles")).toBeInTheDocument();
    });

    it("displays recommendations section", () => {
      expect(screen.getByText("Recommendations")).toBeInTheDocument();
      mockAnalysis.recommendations.forEach((rec) => {
        expect(screen.getByText(rec)).toBeInTheDocument();
      });
    });

    it("displays risks section", () => {
      expect(screen.getByText("Risks")).toBeInTheDocument();
      mockAnalysis.risks.forEach((risk) => {
        expect(screen.getByText(risk)).toBeInTheDocument();
      });
    });

    it("displays generated timestamp", () => {
      expect(screen.getByText(/Generated:/)).toBeInTheDocument();
    });
  });

  describe("Section Expansion/Collapse", () => {
    beforeEach(async () => {
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(mockAnalysis.summary)).toBeInTheDocument();
      });
    });

    it("all sections are expanded by default", () => {
      expect(screen.getByText(mockAnalysis.summary)).toBeVisible();
      expect(screen.getByText("$150.25")).toBeVisible();
      expect(screen.getByText("0.75")).toBeVisible();
    });

    it("collapses section when header is clicked", () => {
      const summaryHeader = screen.getByText("Summary").closest("button");
      expect(summaryHeader).toBeInTheDocument();

      fireEvent.click(summaryHeader!);

      // Summary content should not be visible after collapse
      const summaryContent = screen.queryByText(mockAnalysis.summary);
      expect(summaryContent).not.toBeInTheDocument();
    });

    it("expands section when header is clicked again", () => {
      const summaryHeader = screen.getByText("Summary").closest("button");

      // Collapse
      fireEvent.click(summaryHeader!);
      expect(screen.queryByText(mockAnalysis.summary)).not.toBeInTheDocument();

      // Expand
      fireEvent.click(summaryHeader!);
      expect(screen.getByText(mockAnalysis.summary)).toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("displays error message when analysis fails", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockRejectedValue(new Error("Analysis failed"));

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Analysis Failed")).toBeInTheDocument();
      });
    });

    it("displays explanation of limitations in error", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/insufficient data.*API limitations.*temporary service issues/i)).toBeInTheDocument();
      });
    });

    it("displays retry button on error", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Retry Analysis")).toBeInTheDocument();
      });
    });

    it("retries analysis when retry button is clicked", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockRejectedValueOnce(new Error("API Error")).mockResolvedValueOnce(mockAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Retry Analysis")).toBeInTheDocument();
      });

      const retryButton = screen.getByText("Retry Analysis");
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText(mockAnalysis.summary)).toBeInTheDocument();
      });
    });

    it("clears error when retry is successful", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockRejectedValueOnce(new Error("API Error")).mockResolvedValueOnce(mockAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Analysis Failed")).toBeInTheDocument();
      });

      const retryButton = screen.getByText("Retry Analysis");
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.queryByText("Analysis Failed")).not.toBeInTheDocument();
        expect(screen.getByText(mockAnalysis.summary)).toBeInTheDocument();
      });
    });
  });

  describe("Trend Styling", () => {
    it("applies correct styling for bullish trend", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const trendBadge = screen.getByText("bullish");
        expect(trendBadge).toHaveClass("text-green-600", "bg-green-50");
      });
    });

    it("applies correct styling for bearish trend", async () => {
      const bearishAnalysis = {
        ...mockAnalysis,
        price_analysis: {
          ...mockAnalysis.price_analysis,
          trend: "bearish" as const,
        },
      };
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(bearishAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const trendBadge = screen.getByText("bearish");
        expect(trendBadge).toHaveClass("text-red-600", "bg-red-50");
      });
    });

    it("applies correct styling for neutral trend", async () => {
      const neutralAnalysis = {
        ...mockAnalysis,
        price_analysis: {
          ...mockAnalysis.price_analysis,
          trend: "neutral" as const,
        },
      };
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(neutralAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const trendBadge = screen.getByText("neutral");
        expect(trendBadge).toHaveClass("text-gray-600", "bg-gray-50");
      });
    });
  });

  describe("Sentiment Styling", () => {
    it("applies correct styling for positive sentiment", async () => {
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const sentimentBadge = screen.getByText("positive");
        expect(sentimentBadge).toHaveClass("text-green-600", "bg-green-50");
      });
    });

    it("applies correct styling for negative sentiment", async () => {
      const negativeAnalysis = {
        ...mockAnalysis,
        sentiment_analysis: {
          ...mockAnalysis.sentiment_analysis,
          overall: "negative" as const,
        },
      };
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(negativeAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const sentimentBadge = screen.getByText("negative");
        expect(sentimentBadge).toHaveClass("text-red-600", "bg-red-50");
      });
    });
  });

  describe("Volatility Styling", () => {
    it("applies correct styling for high volatility", async () => {
      const highVolAnalysis = {
        ...mockAnalysis,
        price_analysis: {
          ...mockAnalysis.price_analysis,
          volatility: "high" as const,
        },
      };
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(highVolAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const volBadge = screen.getByText("high");
        expect(volBadge).toHaveClass("text-red-600", "bg-red-50");
      });
    });

    it("applies correct styling for low volatility", async () => {
      const lowVolAnalysis = {
        ...mockAnalysis,
        price_analysis: {
          ...mockAnalysis.price_analysis,
          volatility: "low" as const,
        },
      };
      (analysisApi.analyzeStock as jest.Mock).mockResolvedValue(lowVolAnalysis);

      render(<StockAnalysisPanel ticker="AAPL" />);

      const analyzeButton = screen.getByRole("button", { name: /analyze/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const volBadge = screen.getByText("low");
        expect(volBadge).toHaveClass("text-green-600", "bg-green-50");
      });
    });
  });
});
