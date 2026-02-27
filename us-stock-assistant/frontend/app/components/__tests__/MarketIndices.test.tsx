import React from "react";
import { render, screen } from "@testing-library/react";
import MarketIndices from "../MarketIndices";
import type { MarketIndex } from "@/app/types/market";

const mockIndices: MarketIndex[] = [
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
    change: -50.0,
    change_percent: -0.36,
  },
  {
    name: "DOW",
    symbol: "^DJI",
    value: 35000.0,
    change: 0.0,
    change_percent: 0.0,
  },
];

describe("MarketIndices Component", () => {
  describe("Component Rendering", () => {
    it("renders the component with title", () => {
      render(<MarketIndices indices={mockIndices} />);
      expect(screen.getByText("Major Market Indices")).toBeInTheDocument();
    });

    it("renders all provided indices", () => {
      render(<MarketIndices indices={mockIndices} />);
      expect(screen.getByText("S&P 500")).toBeInTheDocument();
      expect(screen.getByText("NASDAQ")).toBeInTheDocument();
      expect(screen.getByText("DOW")).toBeInTheDocument();
    });

    it("displays index symbols", () => {
      render(<MarketIndices indices={mockIndices} />);
      expect(screen.getByText("^GSPC")).toBeInTheDocument();
      expect(screen.getByText("^IXIC")).toBeInTheDocument();
      expect(screen.getByText("^DJI")).toBeInTheDocument();
    });
  });

  describe("Value Display", () => {
    it("displays index values with proper formatting", () => {
      render(<MarketIndices indices={mockIndices} />);
      expect(screen.getByText("4,500.00")).toBeInTheDocument();
      expect(screen.getByText("14,000.00")).toBeInTheDocument();
      expect(screen.getByText("35,000.00")).toBeInTheDocument();
    });

    it("displays change values", () => {
      render(<MarketIndices indices={mockIndices} />);
      expect(screen.getByText("+25.50")).toBeInTheDocument();
      expect(screen.getByText("-50.00")).toBeInTheDocument();
      expect(screen.getByText("0.00")).toBeInTheDocument();
    });

    it("displays change percentages", () => {
      render(<MarketIndices indices={mockIndices} />);
      expect(screen.getByText("(+0.57%)")).toBeInTheDocument();
      expect(screen.getByText("(-0.36%)")).toBeInTheDocument();
      expect(screen.getByText("(0.00%)")).toBeInTheDocument();
    });
  });

  describe("Color Coding", () => {
    it("applies green color for positive changes", () => {
      render(<MarketIndices indices={mockIndices} />);
      const positiveChange = screen.getByText("+25.50").parentElement;
      expect(positiveChange).toHaveClass("text-green-600");
    });

    it("applies red color for negative changes", () => {
      render(<MarketIndices indices={mockIndices} />);
      const negativeChange = screen.getByText("-50.00").parentElement;
      expect(negativeChange).toHaveClass("text-red-600");
    });

    it("applies gray color for zero changes", () => {
      render(<MarketIndices indices={mockIndices} />);
      const zeroChange = screen.getByText("0.00").parentElement;
      expect(zeroChange).toHaveClass("text-gray-600");
    });
  });

  describe("Icons", () => {
    it("displays up arrow for positive changes", () => {
      render(<MarketIndices indices={mockIndices} />);
      const positiveChange = screen.getByText("+25.50").parentElement;
      const svg = positiveChange?.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });

    it("displays down arrow for negative changes", () => {
      render(<MarketIndices indices={mockIndices} />);
      const negativeChange = screen.getByText("-50.00").parentElement;
      const svg = negativeChange?.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });

    it("does not display arrow for zero changes", () => {
      render(<MarketIndices indices={mockIndices} />);
      const zeroChange = screen.getByText("0.00").parentElement;
      const svg = zeroChange?.querySelector("svg");
      expect(svg).not.toBeInTheDocument();
    });
  });

  describe("Responsive Layout", () => {
    it("applies grid layout classes", () => {
      const { container } = render(<MarketIndices indices={mockIndices} />);
      const grid = container.querySelector(".grid");
      expect(grid).toHaveClass("grid-cols-1", "md:grid-cols-3");
    });
  });

  describe("Empty State", () => {
    it("renders without errors when indices array is empty", () => {
      render(<MarketIndices indices={[]} />);
      expect(screen.getByText("Major Market Indices")).toBeInTheDocument();
    });
  });
});
