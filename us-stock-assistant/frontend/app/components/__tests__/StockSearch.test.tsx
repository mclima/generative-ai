import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import StockSearch from "../StockSearch";
import { stocksApi } from "@/app/lib/api/stocks";
import type { StockSearchResult } from "@/app/types/stocks";

// Mock the stocks API
jest.mock("@/app/lib/api/stocks", () => ({
  stocksApi: {
    searchStocks: jest.fn(),
  },
}));

const mockSearchResults: StockSearchResult[] = [
  {
    ticker: "AAPL",
    company_name: "Apple Inc.",
    exchange: "NASDAQ",
    relevance_score: 1.0,
  },
  {
    ticker: "MSFT",
    company_name: "Microsoft Corporation",
    exchange: "NASDAQ",
    relevance_score: 0.9,
  },
  {
    ticker: "GOOGL",
    company_name: "Alphabet Inc.",
    exchange: "NASDAQ",
    relevance_score: 0.8,
  },
];

describe("StockSearch Component", () => {
  const mockOnSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Search Input", () => {
    it("renders search input with placeholder", () => {
      render(<StockSearch onSelect={mockOnSelect} placeholder="Search for stocks" />);

      const input = screen.getByPlaceholderText("Search for stocks");
      expect(input).toBeInTheDocument();
    });

    it("accepts text input", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);

      const input = screen.getByRole("textbox");
      await userEvent.type(input, "AAPL");

      expect(input).toHaveValue("AAPL");
    });

    it("uses default placeholder when not provided", () => {
      render(<StockSearch onSelect={mockOnSelect} />);

      const input = screen.getByPlaceholderText("Search stocks...");
      expect(input).toBeInTheDocument();
    });
  });

  describe("Debouncing", () => {
    it("debounces API calls", async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      // Type text
      await userEvent.type(input, "AAPL");

      // Wait for debounce and API call
      await waitFor(
        () => {
          expect(stocksApi.searchStocks).toHaveBeenCalledWith("AAPL");
        },
        { timeout: 1000 },
      );
    });

    it("does not search for empty query", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "   ");

      // Wait a bit to ensure no call is made
      await new Promise((resolve) => setTimeout(resolve, 400));

      expect(stocksApi.searchStocks).not.toHaveBeenCalled();
    });
  });

  describe("Result Rendering", () => {
    it("displays search results after successful search", async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "AAPL");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
        expect(screen.getByText("Apple Inc.")).toBeInTheDocument();
        // Use getAllByText since NASDAQ appears multiple times
        const nasdaqElements = screen.getAllByText("NASDAQ");
        expect(nasdaqElements.length).toBeGreaterThan(0);
      });
    });

    it("displays all search results", async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
        expect(screen.getByText("MSFT")).toBeInTheDocument();
        expect(screen.getByText("GOOGL")).toBeInTheDocument();
      });
    });

    it("displays empty state when no results found", async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue([]);

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "INVALID");

      await waitFor(() => {
        expect(screen.getByText("No stocks found")).toBeInTheDocument();
        expect(screen.getByText("Try a different search term")).toBeInTheDocument();
      });
    });

    it("displays error message when search fails", async () => {
      (stocksApi.searchStocks as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "AAPL");

      // Wait for the search to complete and error to be set
      await waitFor(
        () => {
          // The error is displayed inside the dropdown when isOpen is true
          const errorMessage = screen.queryByText("Failed to search stocks. Please try again.");
          expect(errorMessage).toBeInTheDocument();
        },
        { timeout: 2000 },
      );
    });
  });

  describe("Loading States", () => {
    it("displays loading spinner while searching", async () => {
      let resolveSearch: (value: StockSearchResult[]) => void;
      const searchPromise = new Promise<StockSearchResult[]>((resolve) => {
        resolveSearch = resolve;
      });
      (stocksApi.searchStocks as jest.Mock).mockReturnValue(searchPromise);

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "AAPL");

      await waitFor(() => {
        const spinner = input.parentElement?.querySelector(".animate-spin");
        expect(spinner).toBeInTheDocument();
      });

      // Resolve the promise
      resolveSearch!(mockSearchResults);
    });

    it("hides loading spinner after results load", async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "AAPL");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      const spinner = input.parentElement?.querySelector(".animate-spin");
      expect(spinner).not.toBeInTheDocument();
    });
  });

  describe("Keyboard Navigation", () => {
    beforeEach(async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);
    });

    it("navigates down through results with ArrowDown", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      // Press ArrowDown to select first item
      fireEvent.keyDown(input, { key: "ArrowDown" });

      const firstResult = screen.getByText("AAPL").closest("button");
      expect(firstResult).toHaveClass("bg-blue-50");

      // Press ArrowDown to select second item
      fireEvent.keyDown(input, { key: "ArrowDown" });

      const secondResult = screen.getByText("MSFT").closest("button");
      expect(secondResult).toHaveClass("bg-blue-50");
    });

    it("navigates up through results with ArrowUp", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      // Navigate down twice
      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "ArrowDown" });

      // Navigate up once
      fireEvent.keyDown(input, { key: "ArrowUp" });

      const firstResult = screen.getByText("AAPL").closest("button");
      expect(firstResult).toHaveClass("bg-blue-50");
    });

    it("selects result with Enter key", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      // Navigate to first result and press Enter
      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "Enter" });

      expect(mockOnSelect).toHaveBeenCalledWith(mockSearchResults[0]);
    });

    it("closes dropdown with Escape key", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      fireEvent.keyDown(input, { key: "Escape" });

      await waitFor(() => {
        expect(screen.queryByText("AAPL")).not.toBeInTheDocument();
      });
    });

    it("does not navigate beyond last result", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      // Navigate down past all results
      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "ArrowDown" });
      fireEvent.keyDown(input, { key: "ArrowDown" }); // Extra press

      const lastResult = screen.getByText("GOOGL").closest("button");
      expect(lastResult).toHaveClass("bg-blue-50");
    });

    it("does not navigate above first result", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      // Try to navigate up from initial position
      fireEvent.keyDown(input, { key: "ArrowUp" });

      // No result should be highlighted
      const results = screen.getAllByRole("option");
      results.forEach((result) => {
        expect(result).not.toHaveClass("bg-blue-50");
      });
    });
  });

  describe("Result Selection", () => {
    beforeEach(async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);
    });

    it("calls onSelect when result is clicked", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "AAPL");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      const result = screen.getByText("AAPL").closest("button");
      fireEvent.click(result!);

      expect(mockOnSelect).toHaveBeenCalledWith(mockSearchResults[0]);
    });

    it("clears input after selection", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox") as HTMLInputElement;

      await userEvent.type(input, "AAPL");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      const result = screen.getByText("AAPL").closest("button");
      fireEvent.click(result!);

      expect(input.value).toBe("");
    });

    it("closes dropdown after selection", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "AAPL");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      const result = screen.getByText("AAPL").closest("button");
      fireEvent.click(result!);

      await waitFor(() => {
        expect(screen.queryByText("Apple Inc.")).not.toBeInTheDocument();
      });
    });

    it("highlights result on mouse hover", async () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      const secondResult = screen.getByText("MSFT").closest("button");
      fireEvent.mouseEnter(secondResult!);

      expect(secondResult).toHaveClass("bg-blue-50");
    });
  });

  describe("Click Outside", () => {
    it("closes dropdown when clicking outside", async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);

      render(
        <div>
          <StockSearch onSelect={mockOnSelect} />
          <div data-testid="outside">Outside element</div>
        </div>,
      );

      const input = screen.getByRole("textbox");

      await userEvent.type(input, "AAPL");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      const outsideElement = screen.getByTestId("outside");
      fireEvent.mouseDown(outsideElement);

      await waitFor(() => {
        expect(screen.queryByText("Apple Inc.")).not.toBeInTheDocument();
      });
    });
  });

  describe("Accessibility", () => {
    it("has proper ARIA attributes", () => {
      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      expect(input).toHaveAttribute("aria-label", "Search stocks");
      expect(input).toHaveAttribute("aria-autocomplete", "list");
      expect(input).toHaveAttribute("aria-controls", "search-results");
      expect(input).toHaveAttribute("aria-expanded", "false");
    });

    it("updates aria-expanded when dropdown opens", async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "AAPL");

      await waitFor(() => {
        expect(input).toHaveAttribute("aria-expanded", "true");
      });
    });

    it("marks selected result with aria-selected", async () => {
      (stocksApi.searchStocks as jest.Mock).mockResolvedValue(mockSearchResults);

      render(<StockSearch onSelect={mockOnSelect} />);
      const input = screen.getByRole("textbox");

      await userEvent.type(input, "tech");

      await waitFor(() => {
        expect(screen.getByText("AAPL")).toBeInTheDocument();
      });

      fireEvent.keyDown(input, { key: "ArrowDown" });

      const firstResult = screen.getByText("AAPL").closest("button");
      expect(firstResult).toHaveAttribute("aria-selected", "true");
    });
  });
});
