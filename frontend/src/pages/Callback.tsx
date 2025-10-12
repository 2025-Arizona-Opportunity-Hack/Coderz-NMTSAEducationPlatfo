import { useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";

/**
 * Auth0 Callback Page
 * This page handles the redirect after Auth0 authentication
 * Auth0 will redirect to this page with a code parameter
 * The Auth0Provider will automatically exchange the code for tokens
 * and then call onRedirectCallback to navigate to the intended destination
 */
export function Callback() {
  const { isLoading, error } = useAuth0();

  useEffect(() => {
    if (error) {
      // Log error for debugging
      /* eslint-disable no-console */
      console.error("Auth0 callback error:", error);
      console.error("Error details:", {
        message: error.message,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        error: (error as any).error,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        error_description: (error as any).error_description,
      });
      console.log(
        "🔧 Troubleshooting steps:",
        "\n1. Check that your Auth0 Application Type is 'Single Page Application'",
        "\n2. Verify http://localhost:5173/callback is in Allowed Callback URLs",
        "\n3. Check Auth0 logs at https://manage.auth0.com/dashboard",
      );
      /* eslint-enable no-console */
    }
  }, [error]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">
            Authentication Error
          </h1>
          <p className="text-gray-600 mb-4">{error.message}</p>
          <a className="text-blue-600 hover:underline" href="/">
            Return to home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
        <p className="mt-4 text-gray-600">
          {isLoading ? "Completing authentication..." : "Redirecting..."}
        </p>
      </div>
    </div>
  );
}
