import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import Sidebar from "../Sidebar";

// Mock Next.js navigation
jest.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
}));

describe("Sidebar Responsive Design", () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
  });

  describe("Mobile Layout", () => {
    beforeEach(() => {
      global.innerWidth = 375;
    });

    it("should be hidden when isOpen is false", () => {
      render(<Sidebar isOpen={false} onClose={mockOnClose} />);

      const sidebar = screen.getByRole("complementary");
      expect(sidebar).toHaveClass("-translate-x-full");
    });

    it("should be visible when isOpen is true", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      const sidebar = screen.getByRole("complementary");
      expect(sidebar).toHaveClass("translate-x-0");
    });

    it("should show close button on mobile when open", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      const closeButton = screen.getByLabelText("Close sidebar");
      expect(closeButton).toBeInTheDocument();
    });

    it("should call onClose when close button is clicked", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      const closeButton = screen.getByLabelText("Close sidebar");
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it("should call onClose when a link is clicked", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      const dashboardLink = screen.getByText("Dashboard");
      fireEvent.click(dashboardLink);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  describe("Navigation Links", () => {
    it("should render all navigation links", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      expect(screen.getByText("Dashboard")).toBeInTheDocument();
      expect(screen.getByText("Portfolio")).toBeInTheDocument();
      expect(screen.getByText("Market Overview")).toBeInTheDocument();
      expect(screen.getByText("Alerts")).toBeInTheDocument();
      expect(screen.getByText("Settings")).toBeInTheDocument();
    });

    it("should highlight active link", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      const dashboardLink = screen.getByText("Dashboard").closest("a");
      expect(dashboardLink).toHaveClass("bg-blue-100", "text-blue-600");
    });

    it("should have touch-friendly spacing", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      const links = screen.getAllByRole("link");
      links.forEach((link) => {
        expect(link).toHaveClass("py-3");
      });
    });
  });

  describe("Responsive Width", () => {
    it("should have fixed width of 256px (w-64)", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      const sidebar = screen.getByRole("complementary");
      expect(sidebar).toHaveClass("w-64");
    });
  });

  describe("Transitions", () => {
    it("should have smooth transition classes", () => {
      render(<Sidebar isOpen={true} onClose={mockOnClose} />);

      const sidebar = screen.getByRole("complementary");
      expect(sidebar).toHaveClass("transition-transform", "duration-300", "ease-in-out");
    });
  });
});
