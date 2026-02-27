import { apiClient } from "../api-client";

export interface UserDataExport {
  export_date: string;
  user: {
    id: string;
    email: string;
    created_at: string;
    updated_at: string;
  };
  portfolio: any;
  alerts: any[];
  preferences: any;
  notifications: any[];
  policy_acceptances: any[];
}

export interface DeletionStatus {
  has_pending_deletion: boolean;
  scheduled_deletion_date?: string;
  requested_at?: string;
}

export const complianceApi = {
  /**
   * Export all user data (GDPR/CCPA compliance)
   */
  async exportData(): Promise<UserDataExport> {
    const response = await apiClient.get("/api/compliance/export-data");
    return response.data;
  },

  /**
   * Download user data as JSON file
   */
  async downloadData(): Promise<void> {
    const data = await this.exportData();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `my-data-${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  /**
   * Request account deletion
   */
  async requestDeletion(): Promise<{ message: string; scheduled_deletion_date: string }> {
    const response = await apiClient.post("/api/compliance/request-deletion");
    return response.data;
  },

  /**
   * Cancel pending account deletion
   */
  async cancelDeletion(): Promise<{ message: string }> {
    const response = await apiClient.post("/api/compliance/cancel-deletion");
    return response.data;
  },

  /**
   * Get deletion status
   */
  async getDeletionStatus(): Promise<DeletionStatus> {
    const response = await apiClient.get("/api/compliance/deletion-status");
    return response.data;
  },

  /**
   * Record policy acceptance
   */
  async recordPolicyAcceptance(policyType: "privacy_policy" | "terms_of_service", policyVersion: string): Promise<void> {
    await apiClient.post("/api/compliance/policy-acceptance", null, {
      params: { policy_type: policyType, policy_version: policyVersion },
    });
  },
};
