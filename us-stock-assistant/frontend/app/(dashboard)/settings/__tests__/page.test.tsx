import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import SettingsPage from "../page";
import { preferencesApi } from "@/app/lib/api";

// Mock the API
jest.mock("@/app/lib/api", () => ({
  preferencesApi: {
    getPreferences: jest.fn(),
    updatePreferences: jest.fn(),
    resetPreferences: jest.fn(),
  },
}));

const mockPreferences = {
  default_chart_type: "line" as const,
  default_time_range: "1M" as const,
  preferred_news_sources: ["Bloomberg", "Reuters"],
  notification_settings: {
    in_app: true,
    email: false,
    push: false,
    alert_types: {
      price_alerts: true,
      news_updates: true,
      portfolio_changes: false,
    },
  },
  refresh_interval: 60,
};

describe("SettingsPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Loading and Display", () => {
    it("should display loading state initially", () => {
      (preferencesApi.getPreferences as jest.Mock).mockImplementation(() => new Promise(() => {}));

      render(<SettingsPage />);
      expect(screen.getByText("Loading preferences...")).toBeInTheDocument();
    });

    it("should load and display preferences", async () => {
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText("Settings")).toBeInTheDocument();
      });

      // Check chart preferences
      const chartTypeSelect = screen.getByLabelText("Default Chart Type") as HTMLSelectElement;
      expect(chartTypeSelect.value).toBe("line");

      const timeRangeSelect = screen.getByLabelText("Default Time Range") as HTMLSelectElement;
      expect(timeRangeSelect.value).toBe("1M");

      // Check news sources
      const bloombergCheckbox = screen.getByLabelText("Bloomberg") as HTMLInputElement;
      expect(bloombergCheckbox.checked).toBe(true);

      const reutersCheckbox = screen.getByLabelText("Reuters") as HTMLInputElement;
      expect(reutersCheckbox.checked).toBe(true);

      // Check notification settings
      const inAppCheckbox = screen.getByLabelText("In-App Notifications") as HTMLInputElement;
      expect(inAppCheckbox.checked).toBe(true);

      const emailCheckbox = screen.getByLabelText("Email Notifications") as HTMLInputElement;
      expect(emailCheckbox.checked).toBe(false);
    });

    it("should display error message when loading fails", async () => {
      (preferencesApi.getPreferences as jest.Mock).mockRejectedValue(new Error("Failed to load"));

      render(<SettingsPage />);

      await waitFor(() => {
        expect(screen.getByText("Failed to load preferences")).toBeInTheDocument();
      });
    });
  });

  describe("Preference Updates", () => {
    beforeEach(async () => {
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);
      render(<SettingsPage />);
      await waitFor(() => {
        expect(screen.getByText("Settings")).toBeInTheDocument();
      });
    });

    it("should update chart type preference", async () => {
      const chartTypeSelect = screen.getByLabelText("Default Chart Type");
      fireEvent.change(chartTypeSelect, { target: { value: "candlestick" } });

      expect((chartTypeSelect as HTMLSelectElement).value).toBe("candlestick");
    });

    it("should update time range preference", async () => {
      const timeRangeSelect = screen.getByLabelText("Default Time Range");
      fireEvent.change(timeRangeSelect, { target: { value: "1Y" } });

      expect((timeRangeSelect as HTMLSelectElement).value).toBe("1Y");
    });

    it("should toggle news source selection", async () => {
      const cnbcCheckbox = screen.getByLabelText("CNBC") as HTMLInputElement;
      expect(cnbcCheckbox.checked).toBe(false);

      fireEvent.click(cnbcCheckbox);
      expect(cnbcCheckbox.checked).toBe(true);

      fireEvent.click(cnbcCheckbox);
      expect(cnbcCheckbox.checked).toBe(false);
    });

    it("should toggle notification channel", async () => {
      const emailCheckbox = screen.getByLabelText("Email Notifications") as HTMLInputElement;
      expect(emailCheckbox.checked).toBe(false);

      fireEvent.click(emailCheckbox);
      expect(emailCheckbox.checked).toBe(true);
    });

    it("should toggle alert type", async () => {
      const portfolioChangesCheckbox = screen.getByLabelText("Portfolio Changes") as HTMLInputElement;
      expect(portfolioChangesCheckbox.checked).toBe(false);

      fireEvent.click(portfolioChangesCheckbox);
      expect(portfolioChangesCheckbox.checked).toBe(true);
    });

    it("should update refresh interval", async () => {
      const slider = screen.getByLabelText("Refresh Interval (seconds)") as HTMLInputElement;
      fireEvent.change(slider, { target: { value: "120" } });

      expect(slider.value).toBe("120");
      expect(screen.getByText("120s")).toBeInTheDocument();
    });
  });

  describe("Save Functionality", () => {
    beforeEach(async () => {
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);
      (preferencesApi.updatePreferences as jest.Mock).mockResolvedValue({
        ...mockPreferences,
        default_chart_type: "candlestick",
      });

      render(<SettingsPage />);
      await waitFor(() => {
        expect(screen.getByText("Settings")).toBeInTheDocument();
      });
    });

    it("should save preferences when save button is clicked", async () => {
      const chartTypeSelect = screen.getByLabelText("Default Chart Type");
      fireEvent.change(chartTypeSelect, { target: { value: "candlestick" } });

      const saveButton = screen.getByText("Save Preferences");
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(preferencesApi.updatePreferences).toHaveBeenCalledWith(
          expect.objectContaining({
            default_chart_type: "candlestick",
          }),
        );
      });

      await waitFor(() => {
        expect(screen.getByText("Preferences saved successfully!")).toBeInTheDocument();
      });
    });

    it("should display error message when save fails", async () => {
      (preferencesApi.updatePreferences as jest.Mock).mockRejectedValue(new Error("Save failed"));

      const saveButton = screen.getByText("Save Preferences");
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText("Failed to save preferences. Please try again.")).toBeInTheDocument();
      });
    });

    it("should disable save button while saving", async () => {
      (preferencesApi.updatePreferences as jest.Mock).mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 100)));

      const saveButton = screen.getByText("Save Preferences");
      fireEvent.click(saveButton);

      expect(screen.getByText("Saving...")).toBeInTheDocument();
      expect(saveButton).toBeDisabled();

      await waitFor(() => {
        expect(screen.getByText("Save Preferences")).toBeInTheDocument();
      });
    });
  });

  describe("Reset Functionality", () => {
    const defaultPreferences = {
      default_chart_type: "line" as const,
      default_time_range: "1M" as const,
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

    beforeEach(async () => {
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);
      (preferencesApi.resetPreferences as jest.Mock).mockResolvedValue(defaultPreferences);

      // Mock window.confirm
      global.confirm = jest.fn(() => true);

      render(<SettingsPage />);
      await waitFor(() => {
        expect(screen.getByText("Settings")).toBeInTheDocument();
      });
    });

    it("should reset preferences when reset button is clicked", async () => {
      const resetButton = screen.getByText("Reset to Defaults");
      fireEvent.click(resetButton);

      await waitFor(() => {
        expect(preferencesApi.resetPreferences).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText("Preferences reset to defaults!")).toBeInTheDocument();
      });
    });

    it("should not reset if user cancels confirmation", async () => {
      global.confirm = jest.fn(() => false);

      const resetButton = screen.getByText("Reset to Defaults");
      fireEvent.click(resetButton);

      expect(preferencesApi.resetPreferences).not.toHaveBeenCalled();
    });

    it("should display error message when reset fails", async () => {
      (preferencesApi.resetPreferences as jest.Mock).mockRejectedValue(new Error("Reset failed"));

      const resetButton = screen.getByText("Reset to Defaults");
      fireEvent.click(resetButton);

      await waitFor(() => {
        expect(screen.getByText("Failed to reset preferences. Please try again.")).toBeInTheDocument();
      });
    });
  });

  describe("Validation", () => {
    beforeEach(async () => {
      (preferencesApi.getPreferences as jest.Mock).mockResolvedValue(mockPreferences);
      render(<SettingsPage />);
      await waitFor(() => {
        expect(screen.getByText("Settings")).toBeInTheDocument();
      });
    });

    it("should enforce refresh interval minimum and maximum", async () => {
      const slider = screen.getByLabelText("Refresh Interval (seconds)") as HTMLInputElement;

      // Check min value
      expect(slider.min).toBe("15");

      // Check max value
      expect(slider.max).toBe("300");

      // Check step
      expect(slider.step).toBe("15");
    });

    it("should display refresh interval value in seconds", async () => {
      const slider = screen.getByLabelText("Refresh Interval (seconds)") as HTMLInputElement;
      fireEvent.change(slider, { target: { value: "180" } });

      expect(screen.getByText("180s")).toBeInTheDocument();
    });
  });
});
