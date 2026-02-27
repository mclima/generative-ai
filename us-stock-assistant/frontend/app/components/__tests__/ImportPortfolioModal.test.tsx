/**
 * Unit Tests for ImportPortfolioModal Component
 *
 * Feature: us-stock-assistant
 *
 * These tests verify the import modal functionality including file upload,
 * validation, preview, and error handling.
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ImportPortfolioModal from "../ImportPortfolioModal";
import { portfolioApi } from "@/app/lib/api/portfolio";

// Mock the portfolio API
jest.mock("@/app/lib/api/portfolio");

describe("ImportPortfolioModal", () => {
  const mockPortfolioApi = portfolioApi as jest.Mocked<typeof portfolioApi>;
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should not render when isOpen is false", () => {
    render(<ImportPortfolioModal isOpen={false} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    expect(screen.queryByText("Import Portfolio")).not.toBeInTheDocument();
  });

  it("should render when isOpen is true", () => {
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    expect(screen.getByText("Import Portfolio")).toBeInTheDocument();
  });

  it("should display format selection options", () => {
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    expect(screen.getByLabelText(/CSV/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Excel/i)).toBeInTheDocument();
  });

  it("should display file format requirements", () => {
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    expect(screen.getByText(/File Format Requirements/i)).toBeInTheDocument();
    expect(screen.getByText(/ticker, quantity, purchase_price, purchase_date/i)).toBeInTheDocument();
  });

  it("should allow file selection", async () => {
    const user = userEvent.setup();
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["ticker,quantity,purchase_price,purchase_date\nAAPL,10,150.00,2023-01-01"], "portfolio.csv", {
      type: "text/csv",
    });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    await waitFor(() => {
      expect(screen.getByText("portfolio.csv")).toBeInTheDocument();
    });
  });

  it("should auto-detect CSV format from file extension", async () => {
    const user = userEvent.setup();
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.csv", { type: "text/csv" });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    await waitFor(() => {
      const csvRadio = screen.getByLabelText(/CSV/i) as HTMLInputElement;
      expect(csvRadio.checked).toBe(true);
    });
  });

  it("should auto-detect Excel format from file extension", async () => {
    const user = userEvent.setup();
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.xlsx", {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    await waitFor(() => {
      const excelRadio = screen.getByLabelText(/Excel/i) as HTMLInputElement;
      expect(excelRadio.checked).toBe(true);
    });
  });

  it("should disable Preview Import button when no file is selected", () => {
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const previewButton = screen.getByText("Preview Import");
    expect(previewButton).toBeDisabled();
  });

  it("should enable Preview Import button when file is selected", async () => {
    const user = userEvent.setup();
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.csv", { type: "text/csv" });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    await waitFor(() => {
      const previewButton = screen.getByText("Preview Import");
      expect(previewButton).not.toBeDisabled();
    });
  });

  it("should display validation errors when import validation fails", async () => {
    const user = userEvent.setup();
    const validationErrors = ["Row 1: Invalid ticker symbol 'INVALID'", "Row 2: Quantity must be positive"];

    mockPortfolioApi.importPortfolio.mockResolvedValue({
      success: false,
      imported_count: 0,
      errors: validationErrors,
    });

    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.csv", { type: "text/csv" });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    const previewButton = screen.getByText("Preview Import");
    await user.click(previewButton);

    await waitFor(() => {
      expect(screen.getByText("Validation Errors")).toBeInTheDocument();
      expect(screen.getByText(/Invalid ticker symbol/i)).toBeInTheDocument();
      expect(screen.getByText(/Quantity must be positive/i)).toBeInTheDocument();
    });
  });

  it("should display preview when validation succeeds", async () => {
    const user = userEvent.setup();
    const previewData = {
      positions: [
        {
          ticker: "AAPL",
          quantity: 10,
          purchase_price: 150.0,
          purchase_date: "2023-01-01",
        },
        {
          ticker: "GOOGL",
          quantity: 5,
          purchase_price: 100.0,
          purchase_date: "2023-02-01",
        },
      ],
      total_count: 2,
    };

    mockPortfolioApi.importPortfolio.mockResolvedValue({
      success: true,
      imported_count: 0,
      errors: [],
      preview: previewData,
    });

    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.csv", { type: "text/csv" });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    const previewButton = screen.getByText("Preview Import");
    await user.click(previewButton);

    await waitFor(() => {
      expect(screen.getByText("Import Preview")).toBeInTheDocument();
      expect(screen.getByText(/Ready to import 2 positions/i)).toBeInTheDocument();
      expect(screen.getByText("AAPL")).toBeInTheDocument();
      expect(screen.getByText("GOOGL")).toBeInTheDocument();
    });
  });

  it("should show Confirm Import button in preview mode", async () => {
    const user = userEvent.setup();
    const previewData = {
      positions: [
        {
          ticker: "AAPL",
          quantity: 10,
          purchase_price: 150.0,
          purchase_date: "2023-01-01",
        },
      ],
      total_count: 1,
    };

    mockPortfolioApi.importPortfolio.mockResolvedValue({
      success: true,
      imported_count: 0,
      errors: [],
      preview: previewData,
    });

    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.csv", { type: "text/csv" });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    const previewButton = screen.getByText("Preview Import");
    await user.click(previewButton);

    await waitFor(() => {
      expect(screen.getByText("Confirm Import")).toBeInTheDocument();
    });
  });

  it("should call onSuccess and close modal after successful import", async () => {
    const user = userEvent.setup();
    const previewData = {
      positions: [
        {
          ticker: "AAPL",
          quantity: 10,
          purchase_price: 150.0,
          purchase_date: "2023-01-01",
        },
      ],
      total_count: 1,
    };

    // First call for preview
    mockPortfolioApi.importPortfolio.mockResolvedValueOnce({
      success: true,
      imported_count: 0,
      errors: [],
      preview: previewData,
    });

    // Second call for actual import
    mockPortfolioApi.importPortfolio.mockResolvedValueOnce({
      success: true,
      imported_count: 1,
      errors: [],
    });

    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.csv", { type: "text/csv" });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    const previewButton = screen.getByText("Preview Import");
    await user.click(previewButton);

    await waitFor(() => {
      expect(screen.getByText("Confirm Import")).toBeInTheDocument();
    });

    const confirmButton = screen.getByText("Confirm Import");
    await user.click(confirmButton);

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it("should allow going back from preview to file selection", async () => {
    const user = userEvent.setup();
    const previewData = {
      positions: [
        {
          ticker: "AAPL",
          quantity: 10,
          purchase_price: 150.0,
          purchase_date: "2023-01-01",
        },
      ],
      total_count: 1,
    };

    mockPortfolioApi.importPortfolio.mockResolvedValue({
      success: true,
      imported_count: 0,
      errors: [],
      preview: previewData,
    });

    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.csv", { type: "text/csv" });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    const previewButton = screen.getByText("Preview Import");
    await user.click(previewButton);

    await waitFor(() => {
      expect(screen.getByText("Import Preview")).toBeInTheDocument();
    });

    const backButtons = screen.getAllByText("Back");
    await user.click(backButtons[0]);

    await waitFor(() => {
      expect(screen.getByText("File Format Requirements")).toBeInTheDocument();
      expect(screen.queryByText("Import Preview")).not.toBeInTheDocument();
    });
  });

  it("should call onClose when close button is clicked", async () => {
    const user = userEvent.setup();
    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const closeButton = screen.getByRole("button", { name: "" }).closest("button");
    if (closeButton) {
      await user.click(closeButton);
    }

    expect(mockOnClose).toHaveBeenCalled();
  });

  it("should display error message when import API call fails", async () => {
    const user = userEvent.setup();
    mockPortfolioApi.importPortfolio.mockRejectedValue(new Error("Network error"));

    render(<ImportPortfolioModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />);

    const file = new File(["data"], "portfolio.csv", { type: "text/csv" });

    const chooseFileButton = screen.getByText("Choose File");
    await user.click(chooseFileButton);

    const fileInput = screen.getByRole("button", { name: /Choose File/i }).previousElementSibling as HTMLInputElement;
    await user.upload(fileInput, file);

    const previewButton = screen.getByText("Preview Import");
    await user.click(previewButton);

    await waitFor(() => {
      expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    });
  });
});
