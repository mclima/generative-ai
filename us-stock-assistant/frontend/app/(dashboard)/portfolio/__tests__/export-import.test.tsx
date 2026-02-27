/**
 * Unit Tests for Portfolio Export/Import Functionality
 *
 * Feature: us-stock-assistant
 *
 * These tests verify the export and import API integration.
 */

import { portfolioApi } from "@/app/lib/api/portfolio";

// Mock the API client
jest.mock("@/app/lib/api-client", () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
  handleApiError: jest.fn((err) => err.message || "An error occurred"),
}));

describe("Portfolio Export/Import API", () => {
  describe("Export Functionality", () => {
    it("should call export API with CSV format", async () => {
      const mockBlob = new Blob(["test data"], { type: "text/csv" });
      const { apiClient } = require("@/app/lib/api-client");
      apiClient.get.mockResolvedValue({ data: mockBlob });

      const result = await portfolioApi.exportPortfolio("csv");

      expect(apiClient.get).toHaveBeenCalledWith("/portfolio/export?format=csv", {
        responseType: "blob",
      });
      expect(result).toBe(mockBlob);
    });

    it("should call export API with Excel format", async () => {
      const mockBlob = new Blob(["test data"], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const { apiClient } = require("@/app/lib/api-client");
      apiClient.get.mockResolvedValue({ data: mockBlob });

      const result = await portfolioApi.exportPortfolio("excel");

      expect(apiClient.get).toHaveBeenCalledWith("/portfolio/export?format=excel", {
        responseType: "blob",
      });
      expect(result).toBe(mockBlob);
    });

    it("should handle export errors", async () => {
      const { apiClient } = require("@/app/lib/api-client");
      apiClient.get.mockRejectedValue(new Error("Export failed"));

      await expect(portfolioApi.exportPortfolio("csv")).rejects.toThrow("Export failed");
    });
  });

  describe("Import Functionality", () => {
    it("should call import API with file and format", async () => {
      const mockFile = new File(["test data"], "portfolio.csv", { type: "text/csv" });
      const mockResponse = {
        success: true,
        imported_count: 5,
        errors: [],
      };
      const { apiClient } = require("@/app/lib/api-client");
      apiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await portfolioApi.importPortfolio(mockFile, "csv");

      expect(apiClient.post).toHaveBeenCalled();
      const callArgs = apiClient.post.mock.calls[0];
      expect(callArgs[0]).toBe("/portfolio/import");
      expect(callArgs[1]).toBeInstanceOf(FormData);
      expect(callArgs[2]).toEqual({ headers: { "Content-Type": "multipart/form-data" } });
      expect(result).toEqual(mockResponse);
    });

    it("should handle validation errors", async () => {
      const mockFile = new File(["invalid data"], "portfolio.csv", { type: "text/csv" });
      const mockResponse = {
        success: false,
        imported_count: 0,
        errors: ["Row 1: Invalid ticker", "Row 2: Negative quantity"],
      };
      const { apiClient } = require("@/app/lib/api-client");
      apiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await portfolioApi.importPortfolio(mockFile, "csv");

      expect(result.success).toBe(false);
      expect(result.errors).toHaveLength(2);
      expect(result.errors[0]).toContain("Invalid ticker");
    });

    it("should handle import errors", async () => {
      const mockFile = new File(["test data"], "portfolio.csv", { type: "text/csv" });
      const { apiClient } = require("@/app/lib/api-client");
      apiClient.post.mockRejectedValue(new Error("Import failed"));

      await expect(portfolioApi.importPortfolio(mockFile, "csv")).rejects.toThrow("Import failed");
    });
  });
});
