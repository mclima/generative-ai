import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import NotificationToast from "../NotificationToast";
import type { Notification } from "@/app/types/notifications";

describe("NotificationToast", () => {
  const mockOnClose = jest.fn();

  const mockNotification: Notification = {
    id: "1",
    user_id: "user1",
    type: "price_alert",
    title: "Price Alert",
    message: "AAPL has reached $150",
    data: { ticker: "AAPL", price: 150 },
    is_read: false,
    created_at: new Date().toISOString(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it("renders notification toast when notification is provided", () => {
    render(<NotificationToast notification={mockNotification} onClose={mockOnClose} />);

    expect(screen.getByText("Price Alert")).toBeInTheDocument();
    expect(screen.getByText("AAPL has reached $150")).toBeInTheDocument();
  });

  it("does not render when notification is null", () => {
    render(<NotificationToast notification={null} onClose={mockOnClose} />);

    expect(screen.queryByText("Price Alert")).not.toBeInTheDocument();
  });

  it("auto-closes after duration", async () => {
    render(<NotificationToast notification={mockNotification} onClose={mockOnClose} duration={3000} />);

    expect(screen.getByText("Price Alert")).toBeInTheDocument();

    // Fast-forward time
    jest.advanceTimersByTime(3300); // Duration + fade out animation

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it("closes when close button is clicked", async () => {
    render(<NotificationToast notification={mockNotification} onClose={mockOnClose} />);

    const closeButton = screen.getByRole("button");
    fireEvent.click(closeButton);

    // Wait for fade out animation
    jest.advanceTimersByTime(300);

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it("displays correct styling for price_alert type", () => {
    render(<NotificationToast notification={mockNotification} onClose={mockOnClose} />);

    const toast = screen.getByText("Price Alert").closest("div");
    expect(toast).toHaveClass("bg-orange-50");
  });

  it("displays correct styling for news_update type", () => {
    const newsNotification: Notification = {
      ...mockNotification,
      type: "news_update",
      title: "News Update",
    };

    render(<NotificationToast notification={newsNotification} onClose={mockOnClose} />);

    const toast = screen.getByText("News Update").closest("div");
    expect(toast).toHaveClass("bg-blue-50");
  });

  it("displays correct styling for portfolio_change type", () => {
    const portfolioNotification: Notification = {
      ...mockNotification,
      type: "portfolio_change",
      title: "Portfolio Change",
    };

    render(<NotificationToast notification={portfolioNotification} onClose={mockOnClose} />);

    const toast = screen.getByText("Portfolio Change").closest("div");
    expect(toast).toHaveClass("bg-green-50");
  });

  it("displays correct icon for each notification type", () => {
    const { rerender } = render(<NotificationToast notification={mockNotification} onClose={mockOnClose} />);

    // Check for price alert icon (bell)
    expect(screen.getByText("Price Alert")).toBeInTheDocument();

    // Test news update icon
    const newsNotification: Notification = {
      ...mockNotification,
      type: "news_update",
      title: "News Update",
    };
    rerender(<NotificationToast notification={newsNotification} onClose={mockOnClose} />);
    expect(screen.getByText("News Update")).toBeInTheDocument();

    // Test portfolio change icon
    const portfolioNotification: Notification = {
      ...mockNotification,
      type: "portfolio_change",
      title: "Portfolio Change",
    };
    rerender(<NotificationToast notification={portfolioNotification} onClose={mockOnClose} />);
    expect(screen.getByText("Portfolio Change")).toBeInTheDocument();
  });

  it("applies fade-in animation when visible", () => {
    render(<NotificationToast notification={mockNotification} onClose={mockOnClose} />);

    const container = screen.getByText("Price Alert").closest(".fixed");
    expect(container).toHaveClass("opacity-100");
    expect(container).toHaveClass("translate-x-0");
  });

  it("respects custom duration", async () => {
    render(<NotificationToast notification={mockNotification} onClose={mockOnClose} duration={1000} />);

    expect(screen.getByText("Price Alert")).toBeInTheDocument();

    jest.advanceTimersByTime(1300); // Duration + fade out animation

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });
});
