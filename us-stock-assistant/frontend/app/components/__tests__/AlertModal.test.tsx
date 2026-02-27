import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import AlertModal from "../AlertModal";
import { alertsApi } from "@/app/lib/api/alerts";
import { stocksApi } from "@/app/lib/api/stocks";

// Mock the API modules
jest.mock("@/app/lib/api/alerts");
jest.mock("@/app/lib/api/stocks");

const mockAlertsApi = alertsApi as jest.Mocked<typeof alertsApi>;
const mockStocksApi = stocksApi as jest.Mocked<typeof stocksApi>;

describe("AlertModal", () => {
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders create alert modal when open", () => {
    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    expect(screen.getByText("Create Price Alert")).toBeInTheDocument();
    expect(screen.getByLabelText("Ticker Symbol")).toBeInTheDocument();
    expect(screen.getByLabelText("Alert Condition")).toBeInTheDocument();
    expect(screen.getByLabelText("Target Price ($)")).toBeInTheDocument();
    expect(screen.getByText("Notification Channels")).toBeInTheDocument();
  });

  it("does not render when closed", () => {
    render(<AlertModal isOpen={false} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    expect(screen.queryByText("Create Price Alert")).not.toBeInTheDocument();
  });

  it("populates form when editing an alert", () => {
    const editAlert = {
      id: "1",
      user_id: "user1",
      ticker: "AAPL",
      condition: "above" as const,
      target_price: 150.0,
      notification_channels: ["in-app" as const, "email" as const],
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
    };

    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} editAlert={editAlert} />);

    expect(screen.getByText("Edit Price Alert")).toBeInTheDocument();
    expect(screen.getByDisplayValue("AAPL")).toBeInTheDocument();
    expect(screen.getByDisplayValue("150")).toBeInTheDocument();
  });

  it("validates required fields", async () => {
    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const submitButton = screen.getByRole("button", { name: /create alert/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Ticker symbol is required")).toBeInTheDocument();
      expect(screen.getByText("Target price is required")).toBeInTheDocument();
    });
  });

  it("validates ticker format", async () => {
    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const tickerInput = screen.getByLabelText("Ticker Symbol");
    fireEvent.change(tickerInput, { target: { value: "INVALID123" } });

    const submitButton = screen.getByRole("button", { name: /create alert/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Invalid ticker symbol format")).toBeInTheDocument();
    });
  });

  it("validates positive target price", async () => {
    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const tickerInput = screen.getByLabelText("Ticker Symbol");
    const priceInput = screen.getByLabelText("Target Price ($)");

    fireEvent.change(tickerInput, { target: { value: "AAPL" } });
    fireEvent.change(priceInput, { target: { value: "-10" } });

    const submitButton = screen.getByRole("button", { name: /create alert/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Target price must be a positive number")).toBeInTheDocument();
    });
  });

  it("creates a new alert successfully", async () => {
    mockAlertsApi.createAlert.mockResolvedValue({
      id: "1",
      user_id: "user1",
      ticker: "AAPL",
      condition: "above",
      target_price: 150.0,
      notification_channels: ["in-app"],
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
    });

    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const tickerInput = screen.getByLabelText("Ticker Symbol");
    const priceInput = screen.getByLabelText("Target Price ($)");

    fireEvent.change(tickerInput, { target: { value: "AAPL" } });
    fireEvent.change(priceInput, { target: { value: "150" } });

    const submitButton = screen.getByRole("button", { name: /create alert/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockAlertsApi.createAlert).toHaveBeenCalledWith({
        ticker: "AAPL",
        condition: "above",
        target_price: 150,
        notification_channels: ["in-app"],
      });
      expect(mockOnSuccess).toHaveBeenCalled();
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it("updates an existing alert successfully", async () => {
    const editAlert = {
      id: "1",
      user_id: "user1",
      ticker: "AAPL",
      condition: "above" as const,
      target_price: 150.0,
      notification_channels: ["in-app" as const],
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
    };

    mockAlertsApi.updateAlert.mockResolvedValue(editAlert);

    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} editAlert={editAlert} />);

    const priceInput = screen.getByLabelText("Target Price ($)");
    fireEvent.change(priceInput, { target: { value: "160" } });

    const submitButton = screen.getByRole("button", { name: /update alert/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockAlertsApi.updateAlert).toHaveBeenCalledWith("1", {
        ticker: "AAPL",
        condition: "above",
        target_price: 160,
        notification_channels: ["in-app"],
      });
      expect(mockOnSuccess).toHaveBeenCalled();
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it("toggles notification channels", () => {
    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const emailCheckbox = screen.getByLabelText("Email Notifications");
    const pushCheckbox = screen.getByLabelText("Push Notifications");

    expect(emailCheckbox).not.toBeChecked();
    expect(pushCheckbox).not.toBeChecked();

    fireEvent.click(emailCheckbox);
    expect(emailCheckbox).toBeChecked();

    fireEvent.click(pushCheckbox);
    expect(pushCheckbox).toBeChecked();

    fireEvent.click(emailCheckbox);
    expect(emailCheckbox).not.toBeChecked();
  });

  it("searches for tickers", async () => {
    mockStocksApi.searchStocks.mockResolvedValue([
      {
        ticker: "AAPL",
        company_name: "Apple Inc.",
        exchange: "NASDAQ",
        relevance_score: 1.0,
      },
      {
        ticker: "AAPLW",
        company_name: "Apple Inc. Warrants",
        exchange: "NASDAQ",
        relevance_score: 0.8,
      },
    ]);

    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const tickerInput = screen.getByLabelText("Ticker Symbol");
    fireEvent.change(tickerInput, { target: { value: "AAPL" } });

    await waitFor(() => {
      expect(mockStocksApi.searchStocks).toHaveBeenCalledWith("AAPL");
      expect(screen.getByText("Apple Inc.")).toBeInTheDocument();
      expect(screen.getByText("Apple Inc. Warrants")).toBeInTheDocument();
    });
  });

  it("selects a ticker from search results", async () => {
    mockStocksApi.searchStocks.mockResolvedValue([
      {
        ticker: "AAPL",
        company_name: "Apple Inc.",
        exchange: "NASDAQ",
        relevance_score: 1.0,
      },
    ]);

    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const tickerInput = screen.getByLabelText("Ticker Symbol");
    fireEvent.change(tickerInput, { target: { value: "AAPL" } });

    await waitFor(() => {
      expect(screen.getByText("Apple Inc.")).toBeInTheDocument();
    });

    const searchResult = screen.getByText("Apple Inc.");
    fireEvent.click(searchResult);

    expect(tickerInput).toHaveValue("AAPL");
    expect(screen.queryByText("Apple Inc.")).not.toBeInTheDocument();
  });

  it("handles API errors gracefully", async () => {
    mockAlertsApi.createAlert.mockRejectedValue(new Error("API Error"));

    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const tickerInput = screen.getByLabelText("Ticker Symbol");
    const priceInput = screen.getByLabelText("Target Price ($)");

    fireEvent.change(tickerInput, { target: { value: "AAPL" } });
    fireEvent.change(priceInput, { target: { value: "150" } });

    const submitButton = screen.getByRole("button", { name: /create alert/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/an unexpected error occurred/i)).toBeInTheDocument();
      expect(mockOnSuccess).not.toHaveBeenCalled();
      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });

  it("closes modal when cancel button is clicked", () => {
    render(<AlertModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });
});
