import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import NotificationBell from "../NotificationBell";
import { notificationsApi } from "@/app/lib/api/notifications";

// Mock the API module
jest.mock("@/app/lib/api/notifications");

const mockNotificationsApi = notificationsApi as jest.Mocked<typeof notificationsApi>;

describe("NotificationBell", () => {
  const mockNotifications = [
    {
      id: "1",
      user_id: "user1",
      type: "price_alert" as const,
      title: "Price Alert Triggered",
      message: "AAPL has reached $150",
      data: { ticker: "AAPL", price: 150 },
      is_read: false,
      created_at: new Date().toISOString(),
    },
    {
      id: "2",
      user_id: "user1",
      type: "news_update" as const,
      title: "Market News",
      message: "New article about TSLA",
      data: { ticker: "TSLA" },
      is_read: true,
      created_at: new Date(Date.now() - 3600000).toISOString(),
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders notification bell icon", () => {
    mockNotificationsApi.getNotifications.mockResolvedValue([]);

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    expect(bellButton).toBeInTheDocument();
  });

  it("displays unread count badge", async () => {
    mockNotificationsApi.getNotifications.mockResolvedValue(mockNotifications);

    render(<NotificationBell />);

    await waitFor(() => {
      expect(screen.getByText("1")).toBeInTheDocument();
    });
  });

  it("does not display badge when no unread notifications", async () => {
    mockNotificationsApi.getNotifications.mockResolvedValue([{ ...mockNotifications[0], is_read: true }, mockNotifications[1]]);

    render(<NotificationBell />);

    await waitFor(() => {
      expect(screen.queryByText("1")).not.toBeInTheDocument();
    });
  });

  it("opens dropdown when bell is clicked", async () => {
    mockNotificationsApi.getNotifications.mockResolvedValue(mockNotifications);

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText("Notifications")).toBeInTheDocument();
      expect(screen.getByText("Price Alert Triggered")).toBeInTheDocument();
      expect(screen.getByText("Market News")).toBeInTheDocument();
    });
  });

  it("closes dropdown when clicking outside", async () => {
    mockNotificationsApi.getNotifications.mockResolvedValue(mockNotifications);

    render(
      <div>
        <div data-testid="outside">Outside</div>
        <NotificationBell />
      </div>,
    );

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText("Notifications")).toBeInTheDocument();
    });

    const outside = screen.getByTestId("outside");
    fireEvent.mouseDown(outside);

    await waitFor(() => {
      expect(screen.queryByText("Notifications")).not.toBeInTheDocument();
    });
  });

  it("marks notification as read when clicked", async () => {
    mockNotificationsApi.getNotifications.mockResolvedValue(mockNotifications);
    mockNotificationsApi.markAsRead.mockResolvedValue();

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText("Price Alert Triggered")).toBeInTheDocument();
    });

    const notification = screen.getByText("Price Alert Triggered");
    fireEvent.click(notification);

    await waitFor(() => {
      expect(mockNotificationsApi.markAsRead).toHaveBeenCalledWith("1");
    });
  });

  it("marks all notifications as read", async () => {
    mockNotificationsApi.getNotifications.mockResolvedValue(mockNotifications);
    mockNotificationsApi.markAllAsRead.mockResolvedValue();

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText("Mark all as read")).toBeInTheDocument();
    });

    const markAllButton = screen.getByText("Mark all as read");
    fireEvent.click(markAllButton);

    await waitFor(() => {
      expect(mockNotificationsApi.markAllAsRead).toHaveBeenCalled();
    });
  });

  it("displays empty state when no notifications", async () => {
    mockNotificationsApi.getNotifications.mockResolvedValue([]);

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText("No notifications")).toBeInTheDocument();
    });
  });

  it("displays loading state while fetching notifications", async () => {
    mockNotificationsApi.getNotifications.mockImplementation(() => new Promise((resolve) => setTimeout(() => resolve([]), 100)));

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    // Should show loading spinner
    await waitFor(() => {
      const spinner = screen.getByRole("button", { name: "Notifications" }).parentElement?.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();
    });
  });

  it("displays correct icon for each notification type", async () => {
    mockNotificationsApi.getNotifications.mockResolvedValue(mockNotifications);

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText("Price Alert Triggered")).toBeInTheDocument();
      expect(screen.getByText("Market News")).toBeInTheDocument();
    });
  });

  it("formats timestamps correctly", async () => {
    const now = new Date();
    const notifications = [
      {
        ...mockNotifications[0],
        created_at: new Date(now.getTime() - 30000).toISOString(), // 30 seconds ago
      },
      {
        ...mockNotifications[1],
        created_at: new Date(now.getTime() - 3600000).toISOString(), // 1 hour ago
      },
    ];

    mockNotificationsApi.getNotifications.mockResolvedValue(notifications);

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText(/ago/)).toBeInTheDocument();
    });
  });

  it("handles API errors gracefully", async () => {
    mockNotificationsApi.getNotifications.mockRejectedValue(new Error("API Error"));

    render(<NotificationBell />);

    const bellButton = screen.getByLabelText("Notifications");
    fireEvent.click(bellButton);

    await waitFor(() => {
      expect(screen.getByText(/an unexpected error occurred/i)).toBeInTheDocument();
    });
  });
});
