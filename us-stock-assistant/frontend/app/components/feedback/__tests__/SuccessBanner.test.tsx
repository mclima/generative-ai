import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import SuccessBanner from "../SuccessBanner";

/**
 * Validates: Requirements 14.3
 * Tests that success banners display correctly
 */
describe("SuccessBanner", () => {
  it("renders success message", () => {
    render(<SuccessBanner message="Operation completed successfully" />);
    expect(screen.getByText("Operation completed successfully")).toBeInTheDocument();
  });

  it("displays success icon", () => {
    const { container } = render(<SuccessBanner message="Success" />);
    const icon = container.querySelector("svg");
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass("text-green-600");
  });

  it("applies correct styling", () => {
    const { container } = render(<SuccessBanner message="Success" />);
    const banner = container.querySelector(".bg-green-50");
    expect(banner).toBeInTheDocument();
    expect(banner).toHaveClass("border-green-200");
  });

  it("renders dismiss button when onDismiss is provided", () => {
    const mockDismiss = jest.fn();
    render(<SuccessBanner message="Success" onDismiss={mockDismiss} />);

    const dismissButton = screen.getByRole("button");
    expect(dismissButton).toBeInTheDocument();
  });

  it("does not render dismiss button when onDismiss is not provided", () => {
    render(<SuccessBanner message="Success" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("calls onDismiss when dismiss button is clicked", () => {
    const mockDismiss = jest.fn();
    render(<SuccessBanner message="Success" onDismiss={mockDismiss} />);

    const dismissButton = screen.getByRole("button");
    fireEvent.click(dismissButton);

    expect(mockDismiss).toHaveBeenCalledTimes(1);
  });

  it("applies custom className", () => {
    const { container } = render(<SuccessBanner message="Success" className="custom-banner" />);
    expect(container.firstChild).toHaveClass("custom-banner");
  });

  it("renders long messages correctly", () => {
    const longMessage = "This is a very long success message that should still be displayed correctly without breaking the layout.";
    render(<SuccessBanner message={longMessage} />);
    expect(screen.getByText(longMessage)).toBeInTheDocument();
  });
});
