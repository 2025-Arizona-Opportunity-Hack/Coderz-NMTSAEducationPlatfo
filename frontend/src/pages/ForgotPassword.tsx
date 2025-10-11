import { useState, FormEvent } from "react";
import { Link } from "react-router-dom";
import { Mail, AlertCircle, CheckCircle } from "lucide-react";

import { authService } from "../services/auth.service";

export function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await authService.resetPassword(email);
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Failed to send reset email. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-green-100">
            <CheckCircle
              aria-hidden="true"
              className="h-6 w-6 text-green-600"
            />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Check your email
            </h2>
            <p className="mt-3 text-gray-600">
              We&apos;ve sent a password reset link to <strong>{email}</strong>
            </p>
            <p className="mt-2 text-sm text-gray-500">
              Please check your inbox and follow the instructions to reset your
              password.
            </p>
          </div>
          <Link
            className="inline-block mt-6 text-blue-600 hover:text-blue-500 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-2 py-1"
            to="/login"
          >
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
            <Mail aria-hidden="true" className="h-6 w-6 text-blue-600" />
          </div>
          <h1 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Reset your password
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your email address and we&apos;ll send you a link to reset
            your password.
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

          <div>
            <label
              className="block text-sm font-medium text-gray-700"
              htmlFor="email"
            >
              Email address
            </label>
            <input
              required
              autoComplete="email"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              id="email"
              name="email"
              placeholder="you@example.com"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <button
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading}
            type="submit"
          >
            {isLoading ? "Sending..." : "Send reset link"}
          </button>

          <div className="text-center">
            <Link
              className="text-sm text-blue-600 hover:text-blue-500 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-2 py-1"
              to="/login"
            >
              Back to login
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
