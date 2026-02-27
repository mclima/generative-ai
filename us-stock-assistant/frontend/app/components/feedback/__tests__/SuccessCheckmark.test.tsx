import { render, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import SuccessCheckmark from "../SuccessCheckmark";

/**
 * Validates: Requirements 14.3
 * Tests that success checkmark animations display correctly
 */
describe("SuccessCheckmark", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it("does not render when show is false", () => {
    const { container } = render(<SuccessCheckmark show={false} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders when show is true", () => {
    const { container } = render(<SuccessCheckmark show={true} />);
    const checkmark = container.querySelector("svg");
    expect(checkmark).toBeInTheDocument();
  });

  it("renders small size", () => {
    const { container } = render(<SuccessCheckmark show={true} size="sm" />);
    const checkmarkContainer = container.querySelector(".w-12");
    expect(checkmarkContainer).toBeInTheDocument();
  });

  it("renders medium size", () => {
    const { container } = render(<SuccessCheckmark show={true} size="md" />);
    const checkmarkContainer = container.querySelector(".w-16");
    expect(checkmarkContainer).toBeInTheDocument();
  });

  it("renders large size", () => {
    const { container } = render(<SuccessCheckmark show={true} size="lg" />);
    const checkmarkContainer = container.querySelector(".w-24");
    expect(checkmarkContainer).toBeInTheDocument();
  });

  it("displays green background", () => {
    const { container } = render(<SuccessCheckmark show={true} />);
    const checkmarkContainer = container.querySelector(".bg-green-500");
    expect(checkmarkContainer).toBeInTheDocument();
  });

  it("displays checkmark icon", () => {
    const { container } = render(<SuccessCheckmark show={true} />);
    const checkmark = container.querySelector("svg");
    expect(checkmark).toBeInTheDocument();
    expect(checkmark).toHaveClass("text-white");
  });

  it("calls onComplete after duration", async () => {
    const mockOnComplete = jest.fn();
    render(<SuccessCheckmark show={true} onComplete={mockOnComplete} duration={1000} />);

    jest.advanceTimersByTime(1300);

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalled();
    });
  });

  it("respects custom duration", async () => {
    const mockOnComplete = jest.fn();
    render(<SuccessCheckmark show={true} onComplete={mockOnComplete} duration={500} />);

    jest.advanceTimersByTime(800);

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalled();
    });
  });

  it("has overlay background", () => {
    const { container } = render(<SuccessCheckmark show={true} />);
    const overlay = container.querySelector(".bg-black.bg-opacity-30");
    expect(overlay).toBeInTheDocument();
  });

  it("applies animation classes", () => {
    const { container } = render(<SuccessCheckmark show={true} />);
    const checkmarkContainer = container.querySelector(".bg-green-500");
    expect(checkmarkContainer).toHaveClass("transform");
    expect(checkmarkContainer).toHaveClass("transition-all");
  });

  it("hides after duration completes", async () => {
    const { container } = render(<SuccessCheckmark show={true} duration={1000} />);

    expect(container.querySelector("svg")).toBeInTheDocument();

    jest.advanceTimersByTime(1300);

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });
});
