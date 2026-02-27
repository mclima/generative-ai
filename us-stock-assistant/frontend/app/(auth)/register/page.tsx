"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "@/app/contexts/AuthContext";
import { handleApiError } from "@/app/lib/api-client";
import Link from "next/link";

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  acceptPrivacyPolicy: boolean;
  acceptTermsOfService: boolean;
}

// Password strength calculation
function calculatePasswordStrength(password: string): {
  score: number;
  label: string;
  color: string;
} {
  let score = 0;

  if (!password) return { score: 0, label: "None", color: "bg-gray-300" };

  // Length check
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;

  // Character variety checks
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;

  // Determine label and color
  if (score <= 2) return { score, label: "Weak", color: "bg-red-500" };
  if (score <= 4) return { score, label: "Fair", color: "bg-yellow-500" };
  if (score <= 5) return { score, label: "Good", color: "bg-blue-500" };
  return { score, label: "Strong", color: "bg-green-500" };
}

export default function RegisterPage() {
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { register: registerUser } = useAuth();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>();

  const password = watch("password", "");
  const passwordStrength = calculatePasswordStrength(password);

  const onSubmit = async (data: RegisterFormData) => {
    setError("");

    if (data.password !== data.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!data.acceptPrivacyPolicy || !data.acceptTermsOfService) {
      setError("You must accept the Privacy Policy and Terms of Service to register");
      return;
    }

    setIsLoading(true);

    try {
      await registerUser({
        email: data.email,
        password: data.password,
        acceptPrivacyPolicy: data.acceptPrivacyPolicy,
        acceptTermsOfService: data.acceptTermsOfService,
      });
    } catch (err) {
      console.error("Registration error:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full space-y-8">
      <div>
        <h2 className="mt-6 text-center text-3xl font-bold text-white">Create your account</h2>
      </div>
      <form className="mt-8 space-y-6" method="post" onSubmit={handleSubmit(onSubmit)}>
        {error && (
          <div className="rounded-md bg-red-900/20 border border-red-800 p-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300">
              Email address
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              {...register("email", {
                required: "Email is required",
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: "Invalid email address",
                },
              })}
              className={`mt-1 appearance-none block w-full px-3 py-2 border ${errors.email ? "border-red-500" : "border-[#2a2a2a]"} bg-[#1a1a1a] focus:bg-[#2a2a2a] text-white rounded-md shadow-sm placeholder-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm`}
              placeholder="Email address"
            />
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              {...register("password", {
                required: "Password is required",
                minLength: {
                  value: 8,
                  message: "Password must be at least 8 characters",
                },
              })}
              className={`mt-1 appearance-none block w-full px-3 py-2 border ${errors.password ? "border-red-500" : "border-[#2a2a2a]"} bg-[#1a1a1a] focus:bg-[#2a2a2a] text-white rounded-md shadow-sm placeholder-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm`}
              placeholder="Password"
            />
            {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}

            {/* Password strength indicator */}
            {password && (
              <div className="mt-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-400">Password strength:</span>
                  <span className={`text-xs font-medium ${passwordStrength.label === "Weak" ? "text-red-600" : passwordStrength.label === "Fair" ? "text-yellow-600" : passwordStrength.label === "Good" ? "text-blue-600" : "text-green-600"}`}>{passwordStrength.label}</span>
                </div>
                <div className="w-full bg-[#2a2a2a] rounded-full h-2">
                  <div className={`h-2 rounded-full transition-all duration-300 ${passwordStrength.color}`} style={{ width: `${(passwordStrength.score / 6) * 100}%` }} />
                </div>
                <p className="mt-1 text-xs text-gray-500">Use 8+ characters with a mix of letters, numbers &amp; symbols</p>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              autoComplete="new-password"
              {...register("confirmPassword", {
                required: "Please confirm your password",
                validate: (value) => value === password || "Passwords do not match",
              })}
              className={`mt-1 appearance-none block w-full px-3 py-2 border ${errors.confirmPassword ? "border-red-500" : "border-[#2a2a2a]"} bg-[#1a1a1a] focus:bg-[#2a2a2a] text-white rounded-md shadow-sm placeholder-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm`}
              placeholder="Confirm Password"
            />
            {errors.confirmPassword && <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>}
          </div>
        </div>

        {/* Policy Acceptance */}
        <div className="space-y-3">
          <div className="flex items-start">
            <input
              id="acceptPrivacyPolicy"
              type="checkbox"
              {...register("acceptPrivacyPolicy", {
                required: "You must accept the Privacy Policy",
              })}
              className="mt-1 h-4 w-4 appearance-none bg-[#1a1a1a] border border-[#2a2a2a] rounded checked:bg-blue-600 checked:border-blue-600 focus:ring-blue-500 cursor-pointer"
            />
            <label htmlFor="acceptPrivacyPolicy" className="ml-2 block text-sm text-gray-300">
              I accept the{" "}
              <Link href="/privacy-policy" target="_blank" className="text-blue-600 hover:text-blue-800 underline">
                Privacy Policy
              </Link>
            </label>
          </div>
          {errors.acceptPrivacyPolicy && <p className="text-sm text-red-600">{errors.acceptPrivacyPolicy.message}</p>}

          <div className="flex items-start">
            <input
              id="acceptTermsOfService"
              type="checkbox"
              {...register("acceptTermsOfService", {
                required: "You must accept the Terms of Service",
              })}
              className="mt-1 h-4 w-4 appearance-none bg-[#1a1a1a] border border-[#2a2a2a] rounded checked:bg-blue-600 checked:border-blue-600 focus:ring-blue-500 cursor-pointer"
            />
            <label htmlFor="acceptTermsOfService" className="ml-2 block text-sm text-gray-300">
              I accept the{" "}
              <Link href="/terms-of-service" target="_blank" className="text-blue-600 hover:text-blue-800 underline">
                Terms of Service
              </Link>
            </label>
          </div>
          {errors.acceptTermsOfService && <p className="text-sm text-red-600">{errors.acceptTermsOfService.message}</p>}
        </div>

        <div>
          <button type="submit" disabled={isLoading} className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed">
            {isLoading ? "Creating account..." : "Register"}
          </button>
        </div>

        <div className="text-center">
          <Link href="/login" className="text-sm font-medium text-blue-600 hover:text-blue-500">
            Already have an account? Sign in
          </Link>
        </div>
      </form>
    </div>
  );
}
