"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/app/lib/api-client";
import type { User, AuthContextType, LoginCredentials, RegisterCredentials } from "@/app/types/auth";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const response = await apiClient.get("/api/auth/me");
          setUser(response.data);
        } catch (error) {
          // Token invalid, clear it
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      }
      setIsLoading(false);
    };

    loadUser();
  }, []);

  // Set up token refresh interval
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(
      async () => {
        try {
          await refreshToken();
        } catch (error) {
          console.error("Token refresh failed:", error);
          logout();
        }
      },
      14 * 60 * 1000,
    ); // Refresh every 14 minutes

    return () => clearInterval(interval);
  }, [user]);

  const login = async (credentials: LoginCredentials) => {
    const response = await apiClient.post("/api/auth/login", {
      email: credentials.email,
      password: credentials.password,
    });

    const { access_token, refresh_token } = response.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);

    // Fetch user data
    const userResponse = await apiClient.get("/api/auth/me");
    setUser(userResponse.data);

    router.push("/dashboard");
  };

  const register = async (credentials: RegisterCredentials) => {
    await apiClient.post("/api/auth/register", credentials);
    // Auto-login after registration
    await login(credentials);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    router.push("/");
  };

  const refreshToken = async () => {
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) throw new Error("No refresh token");

    const response = await apiClient.post("/api/auth/refresh", {
      refresh_token: refresh,
    });

    const { access_token } = response.data;
    localStorage.setItem("access_token", access_token);
  };

  const demoLogin = async () => {
    const response = await apiClient.post("/api/auth/demo-login");

    const { access_token, refresh_token } = response.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);

    // Fetch user data
    const userResponse = await apiClient.get("/api/auth/me");
    setUser(userResponse.data);

    router.push("/dashboard");
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshToken,
    demoLogin,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
