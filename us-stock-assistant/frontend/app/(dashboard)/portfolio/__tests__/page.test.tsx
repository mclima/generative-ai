/**
 * Unit Tests for Portfolio Export/Import UI
 *
 * Feature: us-stock-assistant
 *
 * These tests verify the export and import functionality of the portfolio page.
 */

import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PortfolioPage from "../page";
import { portfolioApi } from "@/app/lib/api/portfolio";
import type { Portfolio, PortfolioMetrics } from "@/app/types/portfolio";

// Mock dependencies
jest.mock("@/app/lib/api/portfolio");
jest.mock("@/app/hooks/useWebSocket", () => ({
  useWebSocket: () => ({
    isConnected: false,
    subscribe: jest.fn(),
    unsubscribe: jest.fn(),
  }),
}));

jest.mock("@/app/hooks/useDataRefresh", () => ({
  useDataRefresh: jest.fn(),
}));

jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock URL.createObjectURL and URL.revokeObjectURL
global.URL.createObjectURL = jest.fn(() => "mock-url");
global.URL.revokeObjectURL = jest.fn();

describe("Portfolio Export/Import UI", () => {
  const mockPortfolioApi = portfolioApi as jest.Mocked<typeof portfolioApi>;

  const mockPortfolio: Portfolio = {
    id: "portfolio-1",
    user_id: "user-1",
    positions: [
      {
        id: "pos-1",
        ticker: "AAPL",
        quantity: 10,
        purchase_price: 150.0,
        purchase_date: new Date("2023-01-01"),
        current_price: 175.0,
        current_value: 1750.0,
        gain_loss: 250.0,
        gain_loss_percent: 16.67,
      },
      {
        id: "pos-2",
        ticker: "GOOGL",
        quantity: 5,
        purchase_price: 100.0,
        purchase_date: new Date("2023-02-01"),
        current_price: 120.0,
        current_value: 600.0,
        gain_loss: 100.0,
        gain_loss_percent: 20.0,
      },
    ],
    total_value: 2350.0,
    total_gain_loss: 350.0,
    total_gain_loss_percent: 17.5,
    created_at: new Date("2023-01-01"),
    updated_at: new Date("2023-12-01"),
  };

  const mockMetrics: PortfolioMetrics = {
    total_value: 2350.0,
    total_gain_loss: 350.0,
    total_gain_loss_percent: 17.5,
    daily_gain_loss: 50.0,
    diversity_score: 0.8,
    performance_by_period: {
      "1D": 2.1,
      "1W": 3.5,
      "1M": 5.2,
      "3M": 8.7,
      "1Y": 17.5,
      ALL: 17.5,
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockPortfolioApi.getPortfolio.mockResolvedValue(mockPortfolio);
    mockPortfolioApi.getMetrics.mockResolvedValue(mockMetrics);
  });

  describe("Export Functionality", () => {
    it("should display Export button when portfolio has positions", async () => {
      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Export")).toBeInTheDocument();
      });
    });

    it("should disable Export button when portfolio is empty", async () => {
      const emptyPortfolio = { ...mockPortfolio, positions: [] };
      mockPortfolioApi.getPortfolio.mockResolvedValue(emptyPortfolio);

      render(<PortfolioPage />);

      await waitFor(() => {
        const exportButton = screen.getByText("Export");
        expect(exportButton).toBeDisabled();
      });
    });

    it("should show export format dropdown when Export button is clicked", async () => {
      const user = userEvent.setup();
      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Export")).toBeInTheDocument();
      });

      const exportButton = screen.getByText("Export");
      await user.click(exportButton);

      await waitFor(() => {
        expect(screen.getByText("Export as CSV")).toBeInTheDocument();
        expect(screen.getByText("Export as Excel")).toBeInTheDocument();
      });
    });

    it("should trigger CSV export when CSV option is selected", async () => {
      const user = userEvent.setup();
      const mockBlob = new Blob(["test data"], { type: "text/csv" });
      mockPortfolioApi.exportPortfolio.mockResolvedValue(mockBlob);

      // Mock document.createElement and appendChild
      const mockLink = {
        href: "",
        download: "",
        click: jest.fn(),
      };
      const createElementSpy = jest.spyOn(document, "createElement").mockReturnValue(mockLink as any);
      const appendChildSpy = jest.spyOn(document.body, "appendChild").mockImplementation(() => mockLink as any);
      const removeChildSpy = jest.spyOn(document.body, "removeChild").mockImplementation(() => mockLink as any);

      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Export")).toBeInTheDocument();
      });

      const exportButton = screen.getByText("Export");
      await user.click(exportButton);

      await waitFor(() => {
        expect(screen.getByText("Export as CSV")).toBeInTheDocument();
      });

      const csvOption = screen.getByText("Export as CSV");
      await user.click(csvOption);

      await waitFor(() => {
        expect(mockPortfolioApi.exportPortfolio).toHaveBeenCalledWith("csv");
        expect(mockLink.download).toBe("portfolio-export.csv");
        expect(mockLink.click).toHaveBeenCalled();
      });

      createElementSpy.mockRestore();
      appendChildSpy.mockRestore();
      removeChildSpy.mockRestore();
    });

    it("should trigger Excel export when Excel option is selected", async () => {
      const user = userEvent.setup();
      const mockBlob = new Blob(["test data"], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
      mockPortfolioApi.exportPortfolio.mockResolvedValue(mockBlob);

      const mockLink = {
        href: "",
        download: "",
        click: jest.fn(),
      };
      const createElementSpy = jest.spyOn(document, "createElement").mockReturnValue(mockLink as any);
      const appendChildSpy = jest.spyOn(document.body, "appendChild").mockImplementation(() => mockLink as any);
      const removeChildSpy = jest.spyOn(document.body, "removeChild").mockImplementation(() => mockLink as any);

      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Export")).toBeInTheDocument();
      });

      const exportButton = screen.getByText("Export");
      await user.click(exportButton);

      await waitFor(() => {
        expect(screen.getByText("Export as Excel")).toBeInTheDocument();
      });

      const excelOption = screen.getByText("Export as Excel");
      await user.click(excelOption);

      await waitFor(() => {
        expect(mockPortfolioApi.exportPortfolio).toHaveBeenCalledWith("excel");
        expect(mockLink.download).toBe("portfolio-export.xlsx");
        expect(mockLink.click).toHaveBeenCalled();
      });

      createElementSpy.mockRestore();
      appendChildSpy.mockRestore();
      removeChildSpy.mockRestore();
    });

    it("should show success message after successful export", async () => {
      const user = userEvent.setup();
      const mockBlob = new Blob(["test data"], { type: "text/csv" });
      mockPortfolioApi.exportPortfolio.mockResolvedValue(mockBlob);

      const mockLink = {
        href: "",
        download: "",
        click: jest.fn(),
      };
      jest.spyOn(document, "createElement").mockReturnValue(mockLink as any);
      jest.spyOn(document.body, "appendChild").mockImplementation(() => mockLink as any);
      jest.spyOn(document.body, "removeChild").mockImplementation(() => mockLink as any);

      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Export")).toBeInTheDocument();
      });

      const exportButton = screen.getByText("Export");
      await user.click(exportButton);

      const csvOption = screen.getByText("Export as CSV");
      await user.click(csvOption);

      await waitFor(() => {
        expect(screen.getByText("Portfolio exported successfully!")).toBeInTheDocument();
      });
    });

    it("should display error message when export fails", async () => {
      const user = userEvent.setup();
      mockPortfolioApi.exportPortfolio.mockRejectedValue(new Error("Export failed"));

      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Export")).toBeInTheDocument();
      });

      const exportButton = screen.getByText("Export");
      await user.click(exportButton);

      const csvOption = screen.getByText("Export as CSV");
      await user.click(csvOption);

      await waitFor(() => {
        expect(screen.getByText(/Export failed/i)).toBeInTheDocument();
      });
    });
  });

  describe("Import Functionality", () => {
    it("should display Import button", async () => {
      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Import")).toBeInTheDocument();
      });
    });

    it("should open import modal when Import button is clicked", async () => {
      const user = userEvent.setup();
      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Import")).toBeInTheDocument();
      });

      const importButton = screen.getByText("Import");
      await user.click(importButton);

      await waitFor(() => {
        expect(screen.getByText("Import Portfolio")).toBeInTheDocument();
      });
    });

    it("should close import modal when Cancel is clicked", async () => {
      const user = userEvent.setup();
      render(<PortfolioPage />);

      await waitFor(() => {
        expect(screen.getByText("Import")).toBeInTheDocument();
      });

      const importButton = screen.getByText("Import");
      await user.click(importButton);

      await waitFor(() => {
        expect(screen.getByText("Import Portfolio")).toBeInTheDocument();
      });

      const cancelButton = screen.getByText("Cancel");
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText("Import Portfolio")).not.toBeInTheDocument();
      });
    });
  });
});
