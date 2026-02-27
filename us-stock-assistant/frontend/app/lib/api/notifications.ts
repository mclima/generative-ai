import { apiClient } from "../api-client";
import type { Notification } from "@/app/types/notifications";

export const notificationsApi = {
  // Get all user notifications
  async getNotifications(): Promise<Notification[]> {
    const response = await apiClient.get("/api/notifications");
    return response.data;
  },

  // Mark a notification as read
  async markAsRead(id: string): Promise<void> {
    await apiClient.put(`/api/notifications/${id}/read`);
  },

  // Mark all notifications as read
  async markAllAsRead(): Promise<void> {
    const notifications = await this.getNotifications();
    await Promise.all(notifications.filter((n) => !n.is_read).map((n) => this.markAsRead(n.id)));
  },
};
