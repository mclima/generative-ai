import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with default config
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Helper to read a cookie by name
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : null;
}

// Request interceptor to add auth token and CSRF token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Attach CSRF token for state-changing requests
    const method = (config.method || "").toUpperCase();
    if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
      const csrfToken = getCookie("csrf_token");
      if (csrfToken && config.headers) {
        config.headers["X-CSRF-Token"] = csrfToken;
      }
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  },
);

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 403 CSRF token validation errors
    if (error.response?.status === 403 && 
        (error.response?.data as any)?.detail === "CSRF token validation failed" && 
        !originalRequest._retry) {
      originalRequest._retry = true;

      // Clear the invalid CSRF token cookie
      document.cookie = "csrf_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      
      // Remove the CSRF token header from the request
      if (originalRequest.headers) {
        delete originalRequest.headers["X-CSRF-Token"];
      }

      // Retry the request - backend will set a new CSRF token
      return apiClient(originalRequest);
    }

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
          throw new Error("No refresh token available");
        }

        // Attempt to refresh the token
        const response = await axios.post(`${API_URL}/api/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        localStorage.setItem("access_token", access_token);

        // Retry the original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

// Helper function to handle API errors
export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with error
      const detail = error.response.data?.detail;

      // Handle validation errors (array of error objects)
      if (Array.isArray(detail)) {
        return detail.map((err: any) => err.msg || err.message || "Validation error").join(", ");
      }

      // Handle simple error messages
      return detail || error.response.data?.message || "An error occurred";
    } else if (error.request) {
      // Request made but no response
      return "No response from server. Please check your connection.";
    }
  }
  return "An unexpected error occurred";
}
