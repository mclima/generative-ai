import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import ErrorMessage from "../ErrorMessage";

/**
 * Validates: Requirements 14.1, 14.5
 * Tests that error messages are user-friendly and display correctly
 */
describe("ErrorMessage", () => {
  it("renders error message with default props", () => {
    render(<ErrorMessage message="Something went wrong" />);

    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("renders custom title", () => {
    render(<ErrorMessage title="Custom Error" message="Error details" />);

    expect(screen.getByText("Custom Error")).toBeInTheDocument();
  });

  it("renders retry button when onRetry is provided", () => {
    const mockRetry = jest.fn();
    render(<ErrorMessage message="Failed to load" onRetry={mockRetry} />);

    const retryButton = screen.getByText("Try Again");
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(mockRetry).toHaveBeenCalledTimes(1);
  });

  it("does not render retry button when onRetry is not provided", () => {
    render(<ErrorMessage message="Failed to load" />);

    expect(screen.queryByText("Try Again")).not.toBeInTheDocument();
  });

  it("renders error variant with correct styling", () => {
    const { container } = render(<ErrorMessage message="Error" variant="error" />);
    const errorContainer = container.querySelector(".bg-red-50");

    expect(errorContainer).toBeInTheDocument();
    expect(errorContainer).toHaveClass("border-red-200");
  });

  it("renders warning variant with correct styling", () => {
    const { container } = render(<ErrorMessage message="Warning" variant="warning" />);
    const warningContainer = container.querySelector(".bg-orange-50");

    expect(warningContainer).toBeInTheDocument();
    expect(warningContainer).toHaveClass("border-orange-200");
  });

  it("renders info variant with correct styling", () => {
    const { container } = render(<ErrorMessage message="Info" variant="info" />);
    const infoContainer = container.querySelector(".bg-blue-50");

    expect(infoContainer).toBeInTheDocument();
    expect(infoContainer).toHaveClass("border-blue-200");
  });

  it("displays appropriate icon for error variant", () => {
    const { container } = render(<ErrorMessage message="Error" variant="error" />);
    const icon = container.querySelector("svg");

    expect(icon).toBeInTheDocument();
  });

  it("displays appropriate icon for warning variant", () => {
    const { container } = render(<ErrorMessage message="Warning" variant="warning" />);
    const icon = container.querySelector("svg");

    expect(icon).toBeInTheDocument();
  });

  it("displays appropriate icon for info variant", () => {
    const { container } = render(<ErrorMessage message="Info" variant="info" />);
    const icon = container.querySelector("svg");

    expect(icon).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(<ErrorMessage message="Error" className="custom-error" />);
    expect(container.firstChild).toHaveClass("custom-error");
  });

  it("renders long error messages correctly", () => {
    const longMessage = "This is a very long error message that should still be displayed correctly without breaking the layout or causing any visual issues.";
    render(<ErrorMessage message={longMessage} />);

    expect(screen.getByText(longMessage)).toBeInTheDocument();
  });
});
