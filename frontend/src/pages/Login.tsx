import { useState, FormEvent } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { LogIn, AlertCircle } from "lucide-react";

import { authService } from "../services/auth.service";
import { useAuthStore } from "../store/useAuthStore";

export function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setAuth } = useAuthStore();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const from = (location.state as any)?.from?.pathname || "/dashboard";

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const { profile } = await authService.signIn(formData);

      if (profile) {
        setAuth(profile);

        if (profile.role === "instructor") {
          navigate("/instructor/dashboard");
        } else if (profile.role === "admin") {
          navigate("/admin/dashboard");
        } else {
          navigate(from, { replace: true });
        }
      }
    } catch (err: any) {
      setError(
        err.message || "Failed to sign in. Please check your credentials.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
            <LogIn aria-hidden="true" className="h-6 w-6 text-blue-600" />
          </div>
          <h1 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Sign in to your account
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{" "}
            <Link
              className="font-medium text-blue-600 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-1"
              to="/register"
            >
              create a new account
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div
              aria-live="polite"
              className="rounded-md bg-red-50 p-4"
              role="alert"
            >
              <div className="flex">
                <AlertCircle
                  aria-hidden="true"
                  className="h-5 w-5 text-red-400"
                />
                <div className="ml-3">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label
                className="block text-sm font-medium text-gray-700"
                htmlFor="email"
              >
                Email address
              </label>
              <input
                required
                aria-describedby={error ? "login-error" : undefined}
                autoComplete="email"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
              />
            </div>

            <div>
              <label
                className="block text-sm font-medium text-gray-700"
                htmlFor="password"
              >
                Password
              </label>
              <input
                required
                aria-describedby={error ? "login-error" : undefined}
                autoComplete="current-password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm">
              <Link
                className="font-medium text-blue-600 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-1"
                to="/forgot-password"
              >
                Forgot your password?
              </Link>
            </div>
          </div>

          <button
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading}
            type="submit"
          >
            {isLoading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
