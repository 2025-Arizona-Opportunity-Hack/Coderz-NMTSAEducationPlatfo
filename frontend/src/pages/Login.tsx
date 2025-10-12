import { useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { LogIn } from "lucide-react";
import { Spinner } from "@heroui/spinner";
import { Button } from "@heroui/button";

import { useAuthStore } from "../store/useAuthStore";

/**
 * Login Page - Auth0 OAuth Only
 * 
 * Redirects users to Auth0 Universal Login.
 * No local email/password authentication.
 * 
 * @accessibility
 * - Button is keyboard accessible
 * - Loading states are announced
 * - Focus is managed during redirect
 */
export function Login() {
  const { loginWithRedirect, isAuthenticated, isLoading } = useAuth0();
  const { isAuthenticated: localAuth } = useAuthStore();

  // If already authenticated, user will be redirected by ProtectedRoute
  useEffect(() => {
    if (isAuthenticated || localAuth) {
      // User is authenticated, they shouldn't be here
      // Let the auth handler redirect them
    }
  }, [isAuthenticated, localAuth]);

  const handleLogin = async () => {
    try {
      await loginWithRedirect({
        appState: {
          returnTo: window.location.pathname,
        },
      });
    } catch (error) {
      console.error("Login error:", error);
    }
  };

  // Show loading while Auth0 initializes
  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        role="status"
        aria-live="polite"
        aria-label="Loading authentication"
      >
        <div className="text-center">
          <Spinner size="lg" color="primary" label="Loading..." />
          <p className="mt-4 text-default-600 text-sm">
            Preparing sign in...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-primary-100">
            <LogIn aria-hidden="true" className="h-8 w-8 text-primary-600" />
          </div>
          <h1 className="mt-6 text-3xl font-bold text-foreground">
            Welcome to NMTSA Learn
          </h1>
          <p className="mt-2 text-default-600">
            Sign in to access your courses and continue learning
          </p>
        </div>

        <div className="mt-8 space-y-4">
          <Button
            color="primary"
            size="lg"
            startContent={<LogIn className="h-5 w-5" />}
            onPress={handleLogin}
            className="w-full"
            aria-label="Sign in with Auth0"
          >
            Sign In with Auth0
          </Button>

          <p className="text-sm text-default-500">
            By signing in, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>

        <div className="mt-8 pt-6 border-t border-default-200">
          <p className="text-sm text-default-600">
            New to NMTSA Learn? Click "Sign In with Auth0" to create an account.
          </p>
        </div>
      </div>
    </div>
  );
}
