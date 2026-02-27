import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import ProgressIndicator from "../ProgressIndicator";

/**
 * Validates: Requirements 14.2
 * Tests that progress indicators display correctly for long operations
 */
describe("ProgressIndicator", () => {
  it("renders progress bar with correct width", () => {
    const { container } = render(<ProgressIndicator progress={50} />);
    const progressBar = container.querySelector(".bg-blue-600");

    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveStyle({ width: "50%" });
  });

  it("displays percentage by default", () => {
    render(<ProgressIndicator progress={75} />);
    expect(screen.getByText("75%")).toBeInTheDocument();
  });

  it("hides percentage when showPercentage is false", () => {
    render(<ProgressIndicator progress={75} showPercentage={false} />);
    expect(screen.queryByText("75%")).not.toBeInTheDocument();
  });

  it("displays label when provided", () => {
    render(<ProgressIndicator progress={50} label="Loading data..." />);
    expect(screen.getByText("Loading data...")).toBeInTheDocument();
  });

  it("clamps progress to 0-100 range (below 0)", () => {
    const { container } = render(<ProgressIndicator progress={-10} />);
    const progressBar = container.querySelector(".bg-blue-600");

    expect(progressBar).toHaveStyle({ width: "0%" });
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("clamps progress to 0-100 range (above 100)", () => {
    const { container } = render(<ProgressIndicator progress={150} />);
    const progressBar = container.querySelector(".bg-blue-600");

    expect(progressBar).toHaveStyle({ width: "100%" });
    expect(screen.getByText("100%")).toBeInTheDocument();
  });

  it("renders small size", () => {
    const { container } = render(<ProgressIndicator progress={50} size="sm" />);
    const progressBar = container.querySelector(".h-1");

    expect(progressBar).toBeInTheDocument();
  });

  it("renders medium size", () => {
    const { container } = render(<ProgressIndicator progress={50} size="md" />);
    const progressBar = container.querySelector(".h-2");

    expect(progressBar).toBeInTheDocument();
  });

  it("renders large size", () => {
    const { container } = render(<ProgressIndicator progress={50} size="lg" />);
    const progressBar = container.querySelector(".h-3");

    expect(progressBar).toBeInTheDocument();
  });

  it("renders blue color", () => {
    const { container } = render(<ProgressIndicator progress={50} color="blue" />);
    const progressBar = container.querySelector(".bg-blue-600");

    expect(progressBar).toBeInTheDocument();
  });

  it("renders green color", () => {
    const { container } = render(<ProgressIndicator progress={50} color="green" />);
    const progressBar = container.querySelector(".bg-green-600");

    expect(progressBar).toBeInTheDocument();
  });

  it("renders orange color", () => {
    const { container } = render(<ProgressIndicator progress={50} color="orange" />);
    const progressBar = container.querySelector(".bg-orange-600");

    expect(progressBar).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(<ProgressIndicator progress={50} className="custom-progress" />);
    expect(container.firstChild).toHaveClass("custom-progress");
  });

  it("has transition animation", () => {
    const { container } = render(<ProgressIndicator progress={50} />);
    const progressBar = container.querySelector(".bg-blue-600");

    expect(progressBar).toHaveClass("transition-all");
  });
});
