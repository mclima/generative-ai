import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import Header from "../Header";

// Mock Next.js router
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
    pathname: "/",
  }),
}));

// Mock NotificationBell component
jest.mock("../NotificationBell", () => {
  return function MockNotificationBell() {
    return <div data-testid="notification-bell">Bell</div>;
  };
});

// Mock AuthContext
jest.mock("@/app/contexts/AuthContext", () => ({
  useAuth: jest.fn(() => ({
    user: { id: "1", email: "test@example.com", createdAt: new Date(), preferences: {} },
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
    loading: false,
  })),
}));

import { useAuth } from "@/app/contexts/AuthContext";

describe("Header Responsive Design", () => {
  beforeEach(() => {
    // Reset window size
    global.innerWidth = 1024;
    global.innerHeight = 768;
    jest.clearAllMocks();
  });

  describe("Desktop Layout (>= 768px)", () => {
    beforeEach(() => {
      global.innerWidth = 1024;
    });

    it("should show desktop navigation when logged in", () => {
      render(<Header />);

      expect(screen.getByText("Dashboard")).toBeInTheDocument();
      expect(screen.getByText("Portfolio")).toBeInTheDocument();
      expect(screen.getByText("Market")).toBeInTheDocument();
      expect(screen.getByText("Alerts")).toBeInTheDocument();
    });

    it("should show user email and logout button", () => {
      render(<Header />);

      expect(screen.getByText("test@example.com")).toBeInTheDocument();
      expect(screen.getByText("Logout")).toBeInTheDocument();
    });
  });

  describe("Mobile Layout (< 768px)", () => {
    beforeEach(() => {
      global.innerWidth = 375;
      global.innerHeight = 667;
    });

    it("should show mobile menu button", () => {
      render(<Header />);

      const menuButton = screen.getByLabelText("Toggle menu");
      expect(menuButton).toBeInTheDocument();
    });

    it("should open mobile menu when hamburger is clicked", async () => {
      render(<Header />);

      const menuButton = screen.getByLabelText("Toggle menu");
      fireEvent.click(menuButton);

      await waitFor(() => {
        expect(screen.getByText("Dashboard")).toBeVisible();
        expect(screen.getByText("Portfolio")).toBeVisible();
      });
    });

    it("should show notification bell on mobile", () => {
      render(<Header />);

      expect(screen.getByTestId("notification-bell")).toBeInTheDocument();
    });
  });

  describe("Logged Out State", () => {
    it("should show login and register buttons when not logged in", () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: null,
        login: jest.fn(),
        logout: jest.fn(),
        register: jest.fn(),
        loading: false,
      });

      render(<Header />);

      expect(screen.getByText("Login")).toBeInTheDocument();
      expect(screen.getByText("Register")).toBeInTheDocument();
    });

    it("should not show navigation when not logged in", () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: null,
        login: jest.fn(),
        logout: jest.fn(),
        register: jest.fn(),
        loading: false,
      });

      render(<Header />);

      expect(screen.queryByText("Dashboard")).not.toBeInTheDocument();
      expect(screen.queryByText("Portfolio")).not.toBeInTheDocument();
    });
  });
});
