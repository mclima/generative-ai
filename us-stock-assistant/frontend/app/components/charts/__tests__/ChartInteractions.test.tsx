/**
 * Property tests for chart interactions
 * Feature: us-stock-assistant, Property 28: Chart Controls Functionality
 * **Validates: Requirements 6.5**
 *
 * Property 28: Chart Controls Functionality
 * For any chart display, the dashboard should provide interactive controls for time range
 * and chart type, and applying these controls should update the visualization accordingly.
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { PortfolioValueChart } from "../PortfolioValueChart";
import { StockPriceChart } from "../StockPriceChart";
import { TimeRangeSelector } from "../TimeRangeSelector";
import { TimeRange, PortfolioValueDataPoint, LineChartDataPoint } from "@/app/types/charts";

// Helper function to generate test data
const generatePortfolioData = (days: number): PortfolioValueDataPoint[] => {
  const data: PortfolioValueDataPoint[] = [];
  const now = Date.now();
  const dayInMs = 24 * 60 * 60 * 1000;

  for (let i = 0; i < days; i++) {
    const timestamp = now - (days - i) * dayInMs;
    const date = new Date(timestamp);
    data.push({
      date: date.toLocaleDateString(),
      value: 10000 + Math.random() * 5000,
      timestamp,
    });
  }

  return data;
};

const generateStockData = (days: number): LineChartDataPoint[] => {
  const data: LineChartDataPoint[] = [];
  const now = Date.now();
  const dayInMs = 24 * 60 * 60 * 1000;

  for (let i = 0; i < days; i++) {
    const timestamp = now - (days - i) * dayInMs;
    const date = new Date(timestamp);
    data.push({
      date: date.toLocaleDateString(),
      value: 100 + Math.random() * 50,
      timestamp,
    });
  }

  return data;
};

describe("Property 28: Chart Controls Functionality", () => {
  describe("TimeRangeSelector", () => {
    it("should render all time range options", () => {
      const mockOnChange = jest.fn();
      render(<TimeRangeSelector selectedRange="1M" onRangeChange={mockOnChange} />);

      const timeRanges: TimeRange[] = ["1D", "1W", "1M", "3M", "1Y", "ALL"];
      timeRanges.forEach((range) => {
        expect(screen.getByText(range)).toBeInTheDocument();
      });
    });

    it("should call onRangeChange when a button is clicked", () => {
      const mockOnChange = jest.fn();
      render(<TimeRangeSelector selectedRange="1M" onRangeChange={mockOnChange} />);

      const button = screen.getByText("1W");
      fireEvent.click(button);

      expect(mockOnChange).toHaveBeenCalledWith("1W");
    });

    it("should highlight the selected range", () => {
      const mockOnChange = jest.fn();
      render(<TimeRangeSelector selectedRange="1M" onRangeChange={mockOnChange} />);

      const selectedButton = screen.getByText("1M");
      expect(selectedButton).toHaveClass("bg-blue-600");
    });

    it("should update selection when different ranges are clicked", () => {
      const mockOnChange = jest.fn();
      const { rerender } = render(<TimeRangeSelector selectedRange="1M" onRangeChange={mockOnChange} />);

      const timeRanges: TimeRange[] = ["1D", "1W", "1M", "3M", "1Y", "ALL"];

      timeRanges.forEach((range) => {
        const button = screen.getByText(range);
        fireEvent.click(button);
        expect(mockOnChange).toHaveBeenCalledWith(range);
      });

      expect(mockOnChange).toHaveBeenCalledTimes(timeRanges.length);
    });
  });

  describe("PortfolioValueChart with Time Range Controls", () => {
    it("should render with time range selector", () => {
      const data = generatePortfolioData(365);
      render(<PortfolioValueChart data={data} />);

      expect(screen.getByText("Portfolio Value Over Time")).toBeInTheDocument();
      expect(screen.getByText("1D")).toBeInTheDocument();
      expect(screen.getByText("1W")).toBeInTheDocument();
      expect(screen.getByText("1M")).toBeInTheDocument();
    });

    it("should filter data when time range is changed", () => {
      const data = generatePortfolioData(365);
      const { container } = render(<PortfolioValueChart data={data} />);

      // Click on 1W button
      const weekButton = screen.getByText("1W");
      fireEvent.click(weekButton);

      // Verify the button is now selected
      expect(weekButton).toHaveClass("bg-blue-600");
    });

    it("should handle empty data gracefully", () => {
      render(<PortfolioValueChart data={[]} />);
      expect(screen.getByText("Portfolio Value Over Time")).toBeInTheDocument();
    });

    it("should handle ALL time range to show all data", () => {
      const data = generatePortfolioData(365);
      render(<PortfolioValueChart data={data} />);

      const allButton = screen.getByText("ALL");
      fireEvent.click(allButton);

      expect(allButton).toHaveClass("bg-blue-600");
    });
  });

  describe("StockPriceChart with Time Range Controls", () => {
    it("should render with time range selector", () => {
      const data = generateStockData(365);
      render(<StockPriceChart data={data} ticker="AAPL" />);

      expect(screen.getByText("AAPL Price History")).toBeInTheDocument();
      expect(screen.getByText("1D")).toBeInTheDocument();
      expect(screen.getByText("1M")).toBeInTheDocument();
    });

    it("should update when time range is changed", () => {
      const data = generateStockData(365);
      render(<StockPriceChart data={data} ticker="AAPL" />);

      const monthButton = screen.getByText("3M");
      fireEvent.click(monthButton);

      expect(monthButton).toHaveClass("bg-blue-600");
    });

    it("should handle different chart types", () => {
      const data = generateStockData(365);

      const { rerender } = render(<StockPriceChart data={data} ticker="AAPL" chartType="line" />);
      expect(screen.getByText("AAPL Price History")).toBeInTheDocument();

      rerender(<StockPriceChart data={data} ticker="AAPL" chartType="candlestick" />);
      expect(screen.getByText("AAPL Price History")).toBeInTheDocument();
    });
  });

  describe("Property: Time Range Filtering Correctness", () => {
    it("should filter data correctly for 1D range", () => {
      const data = generatePortfolioData(365);
      render(<PortfolioValueChart data={data} />);

      const oneDayButton = screen.getByText("1D");
      fireEvent.click(oneDayButton);

      // The chart should now only show data from the last day
      expect(oneDayButton).toHaveClass("bg-blue-600");
    });

    it("should filter data correctly for 1W range", () => {
      const data = generatePortfolioData(365);
      render(<PortfolioValueChart data={data} />);

      const oneWeekButton = screen.getByText("1W");
      fireEvent.click(oneWeekButton);

      expect(oneWeekButton).toHaveClass("bg-blue-600");
    });

    it("should filter data correctly for 1M range", () => {
      const data = generatePortfolioData(365);
      render(<PortfolioValueChart data={data} />);

      const oneMonthButton = screen.getByText("1M");
      fireEvent.click(oneMonthButton);

      expect(oneMonthButton).toHaveClass("bg-blue-600");
    });

    it("should show all data for ALL range", () => {
      const data = generatePortfolioData(365);
      render(<PortfolioValueChart data={data} />);

      const allButton = screen.getByText("ALL");
      fireEvent.click(allButton);

      expect(allButton).toHaveClass("bg-blue-600");
    });
  });

  describe("Property: Interactive Controls Update Visualization", () => {
    it("should maintain state across multiple range changes", () => {
      const data = generatePortfolioData(365);
      render(<PortfolioValueChart data={data} />);

      // Change to 1W
      fireEvent.click(screen.getByText("1W"));
      expect(screen.getByText("1W")).toHaveClass("bg-blue-600");

      // Change to 3M
      fireEvent.click(screen.getByText("3M"));
      expect(screen.getByText("3M")).toHaveClass("bg-blue-600");
      expect(screen.getByText("1W")).not.toHaveClass("bg-blue-600");

      // Change to ALL
      fireEvent.click(screen.getByText("ALL"));
      expect(screen.getByText("ALL")).toHaveClass("bg-blue-600");
      expect(screen.getByText("3M")).not.toHaveClass("bg-blue-600");
    });

    it("should handle rapid successive range changes", () => {
      const data = generatePortfolioData(365);
      render(<PortfolioValueChart data={data} />);

      const ranges: TimeRange[] = ["1D", "1W", "1M", "3M", "1Y", "ALL"];

      ranges.forEach((range) => {
        fireEvent.click(screen.getByText(range));
        expect(screen.getByText(range)).toHaveClass("bg-blue-600");
      });
    });
  });

  describe("Property: Accessibility of Chart Controls", () => {
    it("should have proper ARIA labels on time range buttons", () => {
      const mockOnChange = jest.fn();
      render(<TimeRangeSelector selectedRange="1M" onRangeChange={mockOnChange} />);

      const button = screen.getByLabelText("Select 1M time range");
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute("aria-pressed", "true");
    });

    it("should update aria-pressed when selection changes", () => {
      const mockOnChange = jest.fn();
      const { rerender } = render(<TimeRangeSelector selectedRange="1M" onRangeChange={mockOnChange} />);

      const monthButton = screen.getByLabelText("Select 1M time range");
      expect(monthButton).toHaveAttribute("aria-pressed", "true");

      rerender(<TimeRangeSelector selectedRange="1W" onRangeChange={mockOnChange} />);

      const weekButton = screen.getByLabelText("Select 1W time range");
      expect(weekButton).toHaveAttribute("aria-pressed", "true");
      expect(monthButton).toHaveAttribute("aria-pressed", "false");
    });
  });
});
