import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import Toast, { ToastMessage } from "../Toast";

/**
 * Validates: Requirements 14.1, 14.3, 14.5
 * Tests that toast notifications display errors and success messages correctly
 */
describe("Toast", () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  const createToast = (type: ToastMessage["type"]): ToastMessage => ({
    id: "test-1",
    type,
    title: `${type} title`,
    message: `${type} message`,
  });

  it("renders success toast", () => {
    const toast = createToast("success");
    render(<Toast toast={toast} onClose={mockOnClose} />);

    expect(screen.getByText("success title")).toBeInTheDocument();
    expect(screen.getByText("success message")).toBeInTheDocument();
  });

  it("renders error toast", () => {
    const toast = createToast("error");
    render(<Toast toast={toast} onClose={mockOnClose} />);

    expect(screen.getByText("error title")).toBeInTheDocument();
    expect(screen.getByText("error message")).toBeInTheDocument();
  });

  it("renders warning toast", () => {
    const toast = createToast("warning");
    render(<Toast toast={toast} onClose={mockOnClose} />);

    expect(screen.getByText("warning title")).toBeInTheDocument();
    expect(screen.getByText("warning message")).toBeInTheDocument();
  });

  it("renders info toast", () => {
    const toast = createToast("info");
    render(<Toast toast={toast} onClose={mockOnClose} />);

    expect(screen.getByText("info title")).toBeInTheDocument();
    expect(screen.getByText("info message")).toBeInTheDocument();
  });

  it("does not render when toast is null", () => {
    render(<Toast toast={null} onClose={mockOnClose} />);

    expect(screen.queryByText("success title")).not.toBeInTheDocument();
  });

  it("applies correct styling for success toast", () => {
    const toast = createToast("success");
    const { container } = render(<Toast toast={toast} onClose={mockOnClose} />);

    const toastElement = container.querySelector(".bg-green-50");
    expect(toastElement).toBeInTheDocument();
    expect(toastElement).toHaveClass("border-green-200");
  });

  it("applies correct styling for error toast", () => {
    const toast = createToast("error");
    const { container } = render(<Toast toast={toast} onClose={mockOnClose} />);

    const toastElement = container.querySelector(".bg-red-50");
    expect(toastElement).toBeInTheDocument();
    expect(toastElement).toHaveClass("border-red-200");
  });

  it("applies correct styling for warning toast", () => {
    const toast = createToast("warning");
    const { container } = render(<Toast toast={toast} onClose={mockOnClose} />);

    const toastElement = container.querySelector(".bg-orange-50");
    expect(toastElement).toBeInTheDocument();
    expect(toastElement).toHaveClass("border-orange-200");
  });

  it("applies correct styling for info toast", () => {
    const toast = createToast("info");
    const { container } = render(<Toast toast={toast} onClose={mockOnClose} />);

    const toastElement = container.querySelector(".bg-blue-50");
    expect(toastElement).toBeInTheDocument();
    expect(toastElement).toHaveClass("border-blue-200");
  });

  it("auto-closes after duration", async () => {
    const toast = createToast("success");
    render(<Toast toast={toast} onClose={mockOnClose} duration={3000} />);

    expect(screen.getByText("success title")).toBeInTheDocument();

    jest.advanceTimersByTime(3300);

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it("closes when close button is clicked", async () => {
    const toast = createToast("success");
    render(<Toast toast={toast} onClose={mockOnClose} />);

    const closeButton = screen.getByRole("button");
    fireEvent.click(closeButton);

    jest.advanceTimersByTime(300);

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it("respects custom duration", async () => {
    const toast = createToast("success");
    render(<Toast toast={toast} onClose={mockOnClose} duration={1000} />);

    jest.advanceTimersByTime(1300);

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it("displays appropriate icon for each type", () => {
    const types: ToastMessage["type"][] = ["success", "error", "warning", "info"];

    types.forEach((type) => {
      const toast = createToast(type);
      const { container } = render(<Toast toast={toast} onClose={mockOnClose} />);

      const icon = container.querySelector("svg");
      expect(icon).toBeInTheDocument();
    });
  });

  it("applies fade-in animation when visible", () => {
    const toast = createToast("success");
    const { container } = render(<Toast toast={toast} onClose={mockOnClose} />);

    const toastContainer = container.querySelector(".fixed");
    expect(toastContainer).toHaveClass("opacity-100");
    expect(toastContainer).toHaveClass("translate-x-0");
  });
});
