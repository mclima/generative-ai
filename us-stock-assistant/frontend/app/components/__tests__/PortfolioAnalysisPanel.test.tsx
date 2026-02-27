import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import PortfolioAnalysisPanel from "../PortfolioAnalysisPanel";
import { analysisApi } from "@/app/lib/api/analysis";
import type { PortfolioAnalysis } from "@/app/types/analysis";

// Mock the analysis API
jest.mock("@/app/lib/api/analysis", () => ({
  analysisApi: {
    analyzePortfolio: jest.fn(),
  },
}));

const mockAnalysis: PortfolioAnalysis = {
  overall_health: "good",
  diversification_score: 75.5,
  risk_level: "medium",
  rebalancing_suggestions: [
    {
      action: "buy",
      ticker: "MSFT",
      reason: "Underweight in technology sector, strong fundamentals",
      suggested_amount: 5000,
    },
    {
      action: "sell",
      ticker: "XYZ",
      reason: "Overweight position, consider taking profits",
      suggested_amount: 2500,
    },
    {
      action: "hold",
      ticker: "AAPL",
      reason: "Well-balanced position, maintain current allocation",
      suggested_amount: 0,
    },
  ],
  underperforming_stocks: ["ABC", "DEF"],
  opportunities: ["Consider adding exposure to healthcare sector", "Emerging markets showing strong growth potential", "Dividend stocks could provide stable income"],
};

describe("PortfolioAnalysisPanel Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Component Rendering", () => {
    it("renders the component with title and analyze button", () => {
      render(<PortfolioAnalysisPanel />);

      expect(screen.getByText("Portfolio Analysis")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /analyze portfolio/i })).toBeInTheDocument();
    });

    it("displays empty state initially", () => {
      render(<PortfolioAnalysisPanel />);

      expect(screen.getByText(/Get AI-Powered Portfolio Insights/i)).toBeInTheDocument();
      expect(screen.getByText(/personalized recommendations.*diversification analysis.*rebalancing suggestions/i)).toBeInTheDocument();
    });
  });

  describe("Analysis Triggering", () => {
    it("calls API when analyze button is clicked", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(analysisApi.analyzePortfolio).toHaveBeenCalled();
      });
    });

    it("disables button during analysis", async () => {
      let resolveAnalysis: (value: PortfolioAnalysis) => void;
      const analysisPromise = new Promise<PortfolioAnalysis>((resolve) => {
        resolveAnalysis = resolve;
      });
      (analysisApi.analyzePortfolio as jest.Mock).mockReturnValue(analysisPromise);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
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
      let resolveAnalysis: (value: PortfolioAnalysis) => void;
      const analysisPromise = new Promise<PortfolioAnalysis>((resolve) => {
        resolveAnalysis = resolve;
      });
      (analysisApi.analyzePortfolio as jest.Mock).mockReturnValue(analysisPromise);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const loadingElements = document.querySelectorAll(".animate-pulse");
        expect(loadingElements.length).toBeGreaterThan(0);
      });

      resolveAnalysis!(mockAnalysis);
    });

    it("hides loading state after analysis completes", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Overall Portfolio Health")).toBeInTheDocument();
      });

      const loadingElements = document.querySelectorAll(".animate-pulse");
      expect(loadingElements.length).toBe(0);
    });
  });

  describe("Overall Health Display", () => {
    it("displays good health status with correct styling", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const healthText = screen.getByText("good");
        expect(healthText).toBeInTheDocument();
        const healthBox = healthText.closest("div.border-2");
        expect(healthBox).toHaveClass("text-green-600", "bg-green-50", "border-green-200");
      });
    });

    it("displays fair health status with correct styling", async () => {
      const fairAnalysis = { ...mockAnalysis, overall_health: "fair" as const };
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(fairAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const healthText = screen.getByText("fair");
        expect(healthText).toBeInTheDocument();
        const healthBox = healthText.closest("div.border-2");
        expect(healthBox).toHaveClass("text-yellow-600", "bg-yellow-50", "border-yellow-200");
      });
    });

    it("displays poor health status with correct styling", async () => {
      const poorAnalysis = { ...mockAnalysis, overall_health: "poor" as const };
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(poorAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const healthText = screen.getByText("poor");
        expect(healthText).toBeInTheDocument();
        const healthBox = healthText.closest("div.border-2");
        expect(healthBox).toHaveClass("text-red-600", "bg-red-50", "border-red-200");
      });
    });
  });

  describe("Diversification Analysis Display", () => {
    beforeEach(async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Diversification Analysis")).toBeInTheDocument();
      });
    });

    it("displays diversification score", () => {
      expect(screen.getByText("75.5")).toBeInTheDocument();
      expect(screen.getByText("/ 100")).toBeInTheDocument();
    });

    it("displays risk level", () => {
      expect(screen.getByText("medium")).toBeInTheDocument();
    });

    it("displays progress bar for diversification score", () => {
      const progressBars = document.querySelectorAll(".bg-gray-200.rounded-full");
      expect(progressBars.length).toBeGreaterThan(0);
    });
  });

  describe("Rebalancing Suggestions Display", () => {
    beforeEach(async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Rebalancing Suggestions")).toBeInTheDocument();
      });
    });

    it("displays all rebalancing suggestions", () => {
      expect(screen.getByText("MSFT")).toBeInTheDocument();
      expect(screen.getByText("XYZ")).toBeInTheDocument();
      expect(screen.getByText("AAPL")).toBeInTheDocument();
    });

    it("displays action badges with correct styling", () => {
      const buyBadge = screen.getByText("buy");
      expect(buyBadge).toHaveClass("text-green-600", "bg-green-50");

      const sellBadge = screen.getByText("sell");
      expect(sellBadge).toHaveClass("text-red-600", "bg-red-50");

      const holdBadge = screen.getByText("hold");
      expect(holdBadge).toHaveClass("text-gray-600", "bg-gray-50");
    });

    it("displays suggestion reasons", () => {
      expect(screen.getByText(/Underweight in technology sector/i)).toBeInTheDocument();
      expect(screen.getByText(/Overweight position/i)).toBeInTheDocument();
      expect(screen.getByText(/Well-balanced position/i)).toBeInTheDocument();
    });

    it("displays suggested amounts", () => {
      expect(screen.getByText("$5000.00")).toBeInTheDocument();
      expect(screen.getByText("$2500.00")).toBeInTheDocument();
    });

    it("displays action buttons for each suggestion", () => {
      const actionButtons = screen.getAllByText("Take Action");
      expect(actionButtons.length).toBe(3);
    });

    it("handles action button clicks", () => {
      const alertSpy = jest.spyOn(window, "alert").mockImplementation(() => {});

      const actionButtons = screen.getAllByText("Take Action");
      fireEvent.click(actionButtons[0]);

      expect(alertSpy).toHaveBeenCalledWith("Action for MSFT: buy");

      alertSpy.mockRestore();
    });
  });

  describe("Underperforming Stocks Display", () => {
    beforeEach(async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Underperforming Stocks")).toBeInTheDocument();
      });
    });

    it("displays underperforming stocks section", () => {
      expect(screen.getByText("Underperforming Stocks")).toBeInTheDocument();
    });

    it("displays all underperforming stock tickers", () => {
      expect(screen.getByText("ABC")).toBeInTheDocument();
      expect(screen.getByText("DEF")).toBeInTheDocument();
    });

    it("applies correct styling to underperforming stocks section", () => {
      const section = screen.getByText("Underperforming Stocks").closest("div.bg-red-50");
      expect(section).toHaveClass("border-red-200");
    });
  });

  describe("Opportunities Display", () => {
    beforeEach(async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Opportunities")).toBeInTheDocument();
      });
    });

    it("displays opportunities section", () => {
      expect(screen.getByText("Opportunities")).toBeInTheDocument();
    });

    it("displays all opportunities", () => {
      mockAnalysis.opportunities.forEach((opportunity) => {
        expect(screen.getByText(opportunity)).toBeInTheDocument();
      });
    });

    it("applies correct styling to opportunities section", () => {
      const section = screen.getByText("Opportunities").closest("div.bg-green-50");
      expect(section).toHaveClass("border-green-200");
    });
  });

  describe("Conditional Rendering", () => {
    it("hides rebalancing suggestions when empty", async () => {
      const noSuggestionsAnalysis = {
        ...mockAnalysis,
        rebalancing_suggestions: [],
      };
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(noSuggestionsAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Overall Portfolio Health")).toBeInTheDocument();
      });

      expect(screen.queryByText("Rebalancing Suggestions")).not.toBeInTheDocument();
    });

    it("hides underperforming stocks when empty", async () => {
      const noUnderperformingAnalysis = {
        ...mockAnalysis,
        underperforming_stocks: [],
      };
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(noUnderperformingAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Overall Portfolio Health")).toBeInTheDocument();
      });

      expect(screen.queryByText("Underperforming Stocks")).not.toBeInTheDocument();
    });

    it("hides opportunities when empty", async () => {
      const noOpportunitiesAnalysis = {
        ...mockAnalysis,
        opportunities: [],
      };
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(noOpportunitiesAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Overall Portfolio Health")).toBeInTheDocument();
      });

      expect(screen.queryByText("Opportunities")).not.toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("displays error message when analysis fails", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockRejectedValue(new Error("Analysis failed"));

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Analysis Failed")).toBeInTheDocument();
      });
    });

    it("displays explanation of limitations in error", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText(/insufficient portfolio data.*API limitations.*temporary service issues/i)).toBeInTheDocument();
      });
    });

    it("displays retry button on error", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Retry Analysis")).toBeInTheDocument();
      });
    });

    it("retries analysis when retry button is clicked", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockRejectedValueOnce(new Error("API Error")).mockResolvedValueOnce(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Retry Analysis")).toBeInTheDocument();
      });

      const retryButton = screen.getByText("Retry Analysis");
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText("Overall Portfolio Health")).toBeInTheDocument();
      });
    });

    it("clears error when retry is successful", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockRejectedValueOnce(new Error("API Error")).mockResolvedValueOnce(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        expect(screen.getByText("Analysis Failed")).toBeInTheDocument();
      });

      const retryButton = screen.getByText("Retry Analysis");
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.queryByText("Analysis Failed")).not.toBeInTheDocument();
        expect(screen.getByText("Overall Portfolio Health")).toBeInTheDocument();
      });
    });
  });

  describe("Risk Level Styling", () => {
    it("applies correct styling for low risk", async () => {
      const lowRiskAnalysis = { ...mockAnalysis, risk_level: "low" as const };
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(lowRiskAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const riskBadge = screen.getByText("low");
        expect(riskBadge).toHaveClass("text-green-600", "bg-green-50");
      });
    });

    it("applies correct styling for medium risk", async () => {
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(mockAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const riskBadge = screen.getByText("medium");
        expect(riskBadge).toHaveClass("text-yellow-600", "bg-yellow-50");
      });
    });

    it("applies correct styling for high risk", async () => {
      const highRiskAnalysis = { ...mockAnalysis, risk_level: "high" as const };
      (analysisApi.analyzePortfolio as jest.Mock).mockResolvedValue(highRiskAnalysis);

      render(<PortfolioAnalysisPanel />);

      const analyzeButton = screen.getByRole("button", { name: /analyze portfolio/i });
      fireEvent.click(analyzeButton);

      await waitFor(() => {
        const riskBadge = screen.getByText("high");
        expect(riskBadge).toHaveClass("text-red-600", "bg-red-50");
      });
    });
  });
});
