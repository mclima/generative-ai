import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import SectorHeatmap from "../SectorHeatmap";
import type { SectorPerformance } from "@/app/types/market";

const mockSectors: SectorPerformance[] = [
  {
    sector: "Technology",
    change_percent: 3.5,
    top_performers: ["AAPL", "MSFT", "GOOGL"],
    bottom_performers: ["IBM"],
  },
  {
    sector: "Healthcare",
    change_percent: 1.2,
    top_performers: ["JNJ", "PFE"],
    bottom_performers: ["CVS"],
  },
  {
    sector: "Energy",
    change_percent: -2.8,
    top_performers: ["XOM"],
    bottom_performers: ["BP", "CVX"],
  },
  {
    sector: "Finance",
    change_percent: 0.0,
    top_performers: ["JPM"],
    bottom_performers: ["WFC"],
  },
];

describe("SectorHeatmap Component", () => {
  describe("Component Rendering", () => {
    it("renders the component with title", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      expect(screen.getByText("Sector Performance Heatmap")).toBeInTheDocument();
    });

    it("renders all provided sectors", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      expect(screen.getByText("Technology")).toBeInTheDocument();
      expect(screen.getByText("Healthcare")).toBeInTheDocument();
      expect(screen.getByText("Energy")).toBeInTheDocument();
      expect(screen.getByText("Finance")).toBeInTheDocument();
    });

    it("displays legend", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      expect(screen.getAllByText("Strong Gain").length).toBeGreaterThan(0);
      expect(screen.getByText("Neutral")).toBeInTheDocument();
      expect(screen.getAllByText("Strong Loss").length).toBeGreaterThan(0);
    });
  });

  describe("Performance Display", () => {
    it("displays sector change percentages", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      expect(screen.getByText("+3.50%")).toBeInTheDocument();
      expect(screen.getByText("+1.20%")).toBeInTheDocument();
      expect(screen.getByText("-2.80%")).toBeInTheDocument();
      expect(screen.getByText("0.00%")).toBeInTheDocument();
    });

    it("displays performance labels", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      expect(screen.getAllByText("Strong Gain").length).toBeGreaterThan(0);
      expect(screen.getByText("Moderate Gain")).toBeInTheDocument();
      expect(screen.getAllByText("Strong Loss").length).toBeGreaterThan(0);
      expect(screen.getByText("Unchanged")).toBeInTheDocument();
    });
  });

  describe("Color Coding", () => {
    it("applies strong green for high positive performance", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const techSector = screen.getByText("Technology").parentElement?.parentElement;
      expect(techSector).toHaveClass("bg-green-600");
    });

    it("applies moderate green for medium positive performance", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const healthSector = screen.getByText("Healthcare").parentElement?.parentElement;
      expect(healthSector).toHaveClass("bg-green-400");
    });

    it("applies red for negative performance", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const energySector = screen.getByText("Energy").parentElement?.parentElement;
      expect(energySector).toHaveClass("bg-red-500");
    });

    it("applies gray for zero performance", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const financeSector = screen.getByText("Finance").parentElement?.parentElement;
      expect(financeSector).toHaveClass("bg-gray-300");
    });
  });

  describe("Hover Tooltips", () => {
    it("displays tooltip on hover", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const techSector = screen.getByText("Technology").closest("div");

      if (techSector) {
        fireEvent.mouseEnter(techSector);
        expect(screen.getByText("Top Performers:")).toBeInTheDocument();
        expect(screen.getByText("AAPL, MSFT, GOOGL")).toBeInTheDocument();
      }
    });

    it("displays bottom performers in tooltip", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const techSector = screen.getByText("Technology").closest("div");

      if (techSector) {
        fireEvent.mouseEnter(techSector);
        expect(screen.getByText("Bottom Performers:")).toBeInTheDocument();
        expect(screen.getByText("IBM")).toBeInTheDocument();
      }
    });

    it("hides tooltip on mouse leave", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const techSector = screen.getByText("Technology").closest("div");

      if (techSector) {
        fireEvent.mouseEnter(techSector);
        expect(screen.getByText("Top Performers:")).toBeInTheDocument();

        fireEvent.mouseLeave(techSector);
        expect(screen.queryByText("Top Performers:")).not.toBeInTheDocument();
      }
    });

    it("shows only one tooltip at a time", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const techSector = screen.getByText("Technology").closest("div");
      const healthSector = screen.getByText("Healthcare").closest("div");

      if (techSector && healthSector) {
        fireEvent.mouseEnter(techSector);
        expect(screen.getByText("AAPL, MSFT, GOOGL")).toBeInTheDocument();

        fireEvent.mouseEnter(healthSector);
        expect(screen.queryByText("AAPL, MSFT, GOOGL")).not.toBeInTheDocument();
        expect(screen.getByText("JNJ, PFE")).toBeInTheDocument();
      }
    });
  });

  describe("Sorting", () => {
    it("sorts sectors by performance (highest to lowest)", () => {
      const { container } = render(<SectorHeatmap sectors={mockSectors} />);
      const sectorElements = container.querySelectorAll(".grid > div");
      const sectorNames = Array.from(sectorElements).map((el) => el.textContent);

      // Technology (3.5%) should be first, Energy (-2.8%) should be last
      expect(sectorNames[0]).toContain("Technology");
      expect(sectorNames[sectorNames.length - 1]).toContain("Energy");
    });
  });

  describe("Responsive Layout", () => {
    it("applies responsive grid layout classes", () => {
      const { container } = render(<SectorHeatmap sectors={mockSectors} />);
      const grid = container.querySelector(".grid");
      expect(grid).toHaveClass("grid-cols-2", "md:grid-cols-3", "lg:grid-cols-4");
    });
  });

  describe("Empty State", () => {
    it("displays empty state message when no sectors provided", () => {
      render(<SectorHeatmap sectors={[]} />);
      expect(screen.getByText("No sector data available")).toBeInTheDocument();
    });

    it("renders without errors when sectors array is empty", () => {
      render(<SectorHeatmap sectors={[]} />);
      expect(screen.getByText("Sector Performance Heatmap")).toBeInTheDocument();
    });
  });

  describe("Hover Effects", () => {
    it("applies hover scale effect", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const techSector = screen.getByText("Technology").parentElement?.parentElement;
      expect(techSector).toHaveClass("hover:scale-105");
    });

    it("applies hover shadow effect", () => {
      render(<SectorHeatmap sectors={mockSectors} />);
      const techSector = screen.getByText("Technology").parentElement?.parentElement;
      expect(techSector).toHaveClass("hover:shadow-lg");
    });
  });
});
