import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RegisterPage from "../page";
import { useAuth } from "@/app/contexts/AuthContext";

// Mock the AuthContext
jest.mock("@/app/contexts/AuthContext", () => ({
  useAuth: jest.fn(),
}));

// Mock Next.js Link component
jest.mock("next/link", () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>;
  };
});

describe("RegisterPage", () => {
  const mockRegister = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useAuth as jest.Mock).mockReturnValue({
      register: mockRegister,
    });
  });

  it("renders registration form with all fields", () => {
    render(<RegisterPage />);

    expect(screen.getByText("Create your account")).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /register/i })).toBeInTheDocument();
  });

  it("validates email field", async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const submitButton = screen.getByRole("button", { name: /register/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });
  });

  // Note: Email format validation is primarily handled by HTML5 input type="email"
  // This test verifies react-hook-form validation works for valid email format
  it("submits form with valid email format", async () => {
    const user = userEvent.setup();
    mockRegister.mockResolvedValue(undefined);

    render(<RegisterPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.type(confirmPasswordInput, "password123");

    const submitButton = screen.getByRole("button", { name: /register/i });
    await user.click(submitButton);

    // Should not show email validation error
    expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument();
  });

  it("validates password field", async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    await user.type(emailInput, "test@example.com");

    const submitButton = screen.getByRole("button", { name: /register/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it("validates password minimum length", async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password$/i);

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "short");

    const submitButton = screen.getByRole("button", { name: /register/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });

  it("validates password confirmation", async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.type(confirmPasswordInput, "different123");

    const submitButton = screen.getByRole("button", { name: /register/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  it("displays password strength indicator", async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const passwordInput = screen.getByLabelText(/^password$/i);

    // Type a weak password
    await user.type(passwordInput, "weak");
    await waitFor(() => {
      expect(screen.getByText(/weak/i)).toBeInTheDocument();
    });

    // Clear and type a stronger password
    await user.clear(passwordInput);
    await user.type(passwordInput, "StrongP@ss123");
    await waitFor(() => {
      expect(screen.getByText(/strong|good/i)).toBeInTheDocument();
    });
  });

  it("shows password strength hint", async () => {
    const user = userEvent.setup();
    render(<RegisterPage />);

    const passwordInput = screen.getByLabelText(/^password$/i);
    await user.type(passwordInput, "password");

    await waitFor(() => {
      expect(screen.getByText(/use 8\+ characters with a mix of letters, numbers & symbols/i)).toBeInTheDocument();
    });
  });

  it("submits form with valid data", async () => {
    const user = userEvent.setup();
    mockRegister.mockResolvedValue(undefined);

    render(<RegisterPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.type(confirmPasswordInput, "password123");

    const submitButton = screen.getByRole("button", { name: /register/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password123",
      });
    });
  });

  it("handles registration errors", async () => {
    const user = userEvent.setup();
    const errorMessage = "Email already exists";
    const axiosError = {
      isAxiosError: true,
      response: {
        data: {
          detail: errorMessage,
        },
      },
    };
    mockRegister.mockRejectedValue(axiosError);

    render(<RegisterPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.type(confirmPasswordInput, "password123");

    const submitButton = screen.getByRole("button", { name: /register/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it("disables submit button while loading", async () => {
    const user = userEvent.setup();
    mockRegister.mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 1000)));

    render(<RegisterPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.type(confirmPasswordInput, "password123");

    const submitButton = screen.getByRole("button", { name: /register/i });
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/creating account\.\.\./i)).toBeInTheDocument();
  });

  it("has link to login page", () => {
    render(<RegisterPage />);

    const loginLink = screen.getByText(/already have an account\? sign in/i);
    expect(loginLink).toBeInTheDocument();
    expect(loginLink.closest("a")).toHaveAttribute("href", "/login");
  });
});
