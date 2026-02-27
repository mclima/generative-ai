import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import Spinner from "../Spinner";

/**
 * Validates: Requirements 14.2
 * Tests that spinner component renders with correct sizes and colors
 */
describe("Spinner", () => {
  it("renders spinner with default props", () => {
    const { container } = render(<Spinner />);
    const spinner = container.querySelector("svg");

    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("animate-spin");
    expect(spinner).toHaveClass("h-6");
    expect(spinner).toHaveClass("w-6");
    expect(spinner).toHaveClass("text-blue-600");
  });

  it("renders small spinner", () => {
    const { container } = render(<Spinner size="sm" />);
    const spinner = container.querySelector("svg");

    expect(spinner).toHaveClass("h-4");
    expect(spinner).toHaveClass("w-4");
  });

  it("renders medium spinner", () => {
    const { container } = render(<Spinner size="md" />);
    const spinner = container.querySelector("svg");

    expect(spinner).toHaveClass("h-6");
    expect(spinner).toHaveClass("w-6");
  });

  it("renders large spinner", () => {
    const { container } = render(<Spinner size="lg" />);
    const spinner = container.querySelector("svg");

    expect(spinner).toHaveClass("h-8");
    expect(spinner).toHaveClass("w-8");
  });

  it("renders with primary color", () => {
    const { container } = render(<Spinner color="primary" />);
    const spinner = container.querySelector("svg");

    expect(spinner).toHaveClass("text-blue-600");
  });

  it("renders with white color", () => {
    const { container } = render(<Spinner color="white" />);
    const spinner = container.querySelector("svg");

    expect(spinner).toHaveClass("text-white");
  });

  it("renders with gray color", () => {
    const { container } = render(<Spinner color="gray" />);
    const spinner = container.querySelector("svg");

    expect(spinner).toHaveClass("text-gray-600");
  });

  it("applies custom className", () => {
    const { container } = render(<Spinner className="custom-spinner" />);
    const spinner = container.querySelector("svg");

    expect(spinner).toHaveClass("custom-spinner");
  });

  it("has spinning animation", () => {
    const { container } = render(<Spinner />);
    const spinner = container.querySelector("svg");

    expect(spinner).toHaveClass("animate-spin");
  });
});
