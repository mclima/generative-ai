import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import SkeletonLoader from "../SkeletonLoader";

/**
 * Validates: Requirements 14.2
 * Tests that skeleton loaders render correctly for different content types
 */
describe("SkeletonLoader", () => {
  it("renders text skeleton by default", () => {
    const { container } = render(<SkeletonLoader />);
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders multiple text skeletons when count is specified", () => {
    const { container } = render(<SkeletonLoader variant="text" count={3} />);
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBe(3);
  });

  it("renders portfolio skeleton with header and positions", () => {
    const { container } = render(<SkeletonLoader variant="portfolio" />);

    // Check for portfolio header skeleton
    const headerSkeleton = container.querySelector(".bg-white.rounded-lg.shadow");
    expect(headerSkeleton).toBeInTheDocument();

    // Check for multiple position skeletons
    const positionSkeletons = container.querySelectorAll(".border-b");
    expect(positionSkeletons.length).toBeGreaterThan(0);
  });

  it("renders chart skeleton with controls", () => {
    const { container } = render(<SkeletonLoader variant="chart" />);

    // Check for chart area
    const chartArea = container.querySelector(".h-64");
    expect(chartArea).toBeInTheDocument();
    expect(chartArea).toHaveClass("animate-pulse");
  });

  it("renders news skeleton with specified count", () => {
    const { container } = render(<SkeletonLoader variant="news" count={3} />);

    // Check for news items
    const newsItems = container.querySelectorAll(".bg-white.rounded-lg.shadow");
    expect(newsItems.length).toBe(3);
  });

  it("renders card skeleton", () => {
    const { container } = render(<SkeletonLoader variant="card" />);

    const cardSkeleton = container.querySelector(".bg-white.rounded-lg.shadow");
    expect(cardSkeleton).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(<SkeletonLoader className="custom-class" />);
    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("all skeleton elements have animate-pulse class", () => {
    const { container } = render(<SkeletonLoader variant="portfolio" />);
    const animatedElements = container.querySelectorAll(".animate-pulse");
    expect(animatedElements.length).toBeGreaterThan(0);
  });
});
