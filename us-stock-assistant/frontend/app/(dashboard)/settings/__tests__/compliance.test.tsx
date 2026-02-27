import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { complianceApi } from "@/app/lib/api";
import SettingsPage from "../page";

// Mock the API
jest.mock("@/app/lib/api", () => ({
  preferencesApi: {
    getPreferences: jest.fn(),
    updatePreferences: jest.fn(),
    resetPreferences: jest.fn(),
  },
  complianceApi: {
    exportData: jest.fn(),
    downloadData: jest.fn(),
    requestDeletion: jest.fn(),
    cancelDeletion: jest.fn(),
    getDeletionStatus: jest.fn(),
  },
}));

describe("Compliance Features in Settings", () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Mock preferences API
    (complianceApi.getDeletionStatus as jest.Mock).mockResolvedValue({
      has_pending_deletion: false,
    });

    const mockPreferences = {
      default_chart_type: "line",
      default_time_range: "1M",
      preferred_news_sources: [],
      notification_settings: {
        in_app: true,
        email: false,
        push: false,
        alert_types: {
          price_alerts: true,
          news_updates: true,
          portfolio_changes: true,
        },
      },
      refresh_interval: 60,
    };

    (require("@/app/lib/api").preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);
  });

  describe("Data Export", () => {
    it("should display download data button", async () => {
      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText("Download My Data")).toBeInTheDocument();
      });
    });

    it("should call downloadData when button is clicked", async () => {
      (complianceApi.downloadData as jest.Mock).mockResolvedValue(undefined);

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText("Download My Data")).toBeInTheDocument();
      });

      const downloadButton = screen.getByText("Download My Data");
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(complianceApi.downloadData).toHaveBeenCalledTimes(1);
      });
    });

    it("should show success message after successful export", async () => {
      (complianceApi.downloadData as jest.Mock).mockResolvedValue(undefined);

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText("Download My Data")).toBeInTheDocument();
      });

      const downloadButton = screen.getByText("Download My Data");
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText(/data has been downloaded successfully/i)).toBeInTheDocument();
      });
    });

    it("should show error message on export failure", async () => {
      (complianceApi.downloadData as jest.Mock).mockRejectedValue(new Error("Export failed"));

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText("Download My Data")).toBeInTheDocument();
      });

      const downloadButton = screen.getByText("Download My Data");
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to export data/i)).toBeInTheDocument();
      });
    });

    it("should disable button while exporting", async () => {
      (complianceApi.downloadData as jest.Mock).mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 100)));

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText("Download My Data")).toBeInTheDocument();
      });

      const downloadButton = screen.getByText("Download My Data");
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText("Exporting...")).toBeInTheDocument();
      });
    });
  });

  describe("Account Deletion", () => {
    it("should display delete account button when no pending deletion", async () => {
      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Delete Account" })).toBeInTheDocument();
      });
    });

    it("should show confirmation dialog before requesting deletion", async () => {
      const confirmSpy = jest.spyOn(window, "confirm").mockReturnValue(false);

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Delete Account" })).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole("button", { name: "Delete Account" });
      fireEvent.click(deleteButton);

      expect(confirmSpy).toHaveBeenCalled();
      expect(complianceApi.requestDeletion).not.toHaveBeenCalled();

      confirmSpy.mockRestore();
    });

    it("should request deletion when confirmed", async () => {
      const confirmSpy = jest.spyOn(window, "confirm").mockReturnValue(true);
      const scheduledDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();

      (complianceApi.requestDeletion as jest.Mock).mockResolvedValue({
        message: "Account deletion scheduled",
        scheduled_deletion_date: scheduledDate,
      });

      (complianceApi.getDeletionStatus as jest.Mock)
        .mockResolvedValueOnce({
          has_pending_deletion: false,
        })
        .mockResolvedValueOnce({
          has_pending_deletion: true,
          scheduled_deletion_date: scheduledDate,
          requested_at: new Date().toISOString(),
        });

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Delete Account" })).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole("button", { name: "Delete Account" });
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(complianceApi.requestDeletion).toHaveBeenCalledTimes(1);
      });

      confirmSpy.mockRestore();
    });

    it("should display pending deletion status", async () => {
      const scheduledDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();

      (complianceApi.getDeletionStatus as jest.Mock).mockResolvedValue({
        has_pending_deletion: true,
        scheduled_deletion_date: scheduledDate,
        requested_at: new Date().toISOString(),
      });

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText(/account deletion scheduled/i)).toBeInTheDocument();
      });

      expect(screen.getByText("Cancel Deletion")).toBeInTheDocument();
    });

    it("should cancel deletion when cancel button is clicked", async () => {
      const confirmSpy = jest.spyOn(window, "confirm").mockReturnValue(true);
      const scheduledDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();

      (complianceApi.getDeletionStatus as jest.Mock)
        .mockResolvedValueOnce({
          has_pending_deletion: true,
          scheduled_deletion_date: scheduledDate,
          requested_at: new Date().toISOString(),
        })
        .mockResolvedValueOnce({
          has_pending_deletion: false,
        });

      (complianceApi.cancelDeletion as jest.Mock).mockResolvedValue({
        message: "Account deletion cancelled",
      });

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText("Cancel Deletion")).toBeInTheDocument();
      });

      const cancelButton = screen.getByText("Cancel Deletion");
      fireEvent.click(cancelButton);

      await waitFor(() => {
        expect(complianceApi.cancelDeletion).toHaveBeenCalledTimes(1);
      });

      confirmSpy.mockRestore();
    });

    it("should show error message on deletion request failure", async () => {
      const confirmSpy = jest.spyOn(window, "confirm").mockReturnValue(true);

      (complianceApi.requestDeletion as jest.Mock).mockRejectedValue(new Error("Deletion failed"));

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Delete Account" })).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole("button", { name: "Delete Account" });
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to request account deletion/i)).toBeInTheDocument();
      });

      confirmSpy.mockRestore();
    });
  });

  describe("Integration", () => {
    it("should allow exporting data before requesting deletion", async () => {
      (complianceApi.downloadData as jest.Mock).mockResolvedValue(undefined);

      const confirmSpy = jest.spyOn(window, "confirm").mockReturnValue(true);
      const scheduledDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();

      (complianceApi.requestDeletion as jest.Mock).mockResolvedValue({
        message: "Account deletion scheduled",
        scheduled_deletion_date: scheduledDate,
      });

      render(<SettingsPage />);

      // First export data
      await waitFor(() => {
        expect(screen.getByText("Download My Data")).toBeInTheDocument();
      });

      const downloadButton = screen.getByText("Download My Data");
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(complianceApi.downloadData).toHaveBeenCalledTimes(1);
      });

      // Then request deletion
      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Delete Account" })).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole("button", { name: "Delete Account" });
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(complianceApi.requestDeletion).toHaveBeenCalledTimes(1);
      });

      confirmSpy.mockRestore();
    });
  });
});
