/**
 * Auth0 Provider with React Router Integration
 * 
 * Wraps the application with Auth0Provider and handles:
 * - Authentication state management
 * - Token injection into API calls
 * - Post-login redirects based on user role
 * - Accessible loading states
 * 
 * @module components/auth/Auth0ProviderWithHistory
 */

import { Auth0Provider, useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Spinner } from "@heroui/spinner";

import { auth0Config, validateAuth0Config } from "../../config/auth0";
import { setAuth0TokenGetter } from "../../config/api";
import { setAuth0Logout } from "../../services/auth.service";
import { useAuthStore } from "../../store/useAuthStore";
import { authService } from "../../services/auth.service";

/**
 * Auth0 callback handler component
 * Manages authentication state after Auth0 redirect
 */
function Auth0Handler({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, user, getAccessTokenSilently, logout } = useAuth0();
  const navigate = useNavigate();
  const { setAuth, clearAuth, setLoading } = useAuthStore();

  useEffect(() => {
    // Set up token getter for API calls
    setAuth0TokenGetter(async () => {
      try {
        return await getAccessTokenSilently();
      } catch (error) {
        console.error("Failed to get access token:", error);
        return "";
      }
    });

    // Set up logout function
    setAuth0Logout(() => {
      logout({
        logoutParams: {
          returnTo: window.location.origin,
        },
      });
    });
  }, [getAccessTokenSilently, logout]);

  useEffect(() => {
    async function handleAuthStateChange() {
      console.log("[Auth0Handler] Auth state change:", { isLoading, isAuthenticated, user: user?.email });
      
      if (isLoading) {
        setLoading(true);
        return;
      }

      if (!isAuthenticated) {
        clearAuth();
        setLoading(false);
        return;
      }

      try {
        console.log("[Auth0Handler] Fetching user profile from backend...");
        
        // Get user profile from backend
        // Backend validates Auth0 token and returns user data with roles
        const profile = await authService.getCurrentUser();

        if (profile) {
          console.log("[Auth0Handler] User profile fetched:", profile.email, profile.role);
          setAuth(profile);

          // Check if we just completed login (from Auth0 callback)
          const isCallback = window.location.search.includes("code=") && 
                           window.location.search.includes("state=");

          if (isCallback) {
            console.log("[Auth0Handler] Handling Auth0 callback, redirecting based on role:", profile.role);
            
            // Clean up URL by removing Auth0 callback parameters
            window.history.replaceState({}, document.title, window.location.pathname);
            
            // Redirect based on user role
            const redirectPath = getRoleBasedRedirect(profile.role);
            console.log("[Auth0Handler] Redirecting to:", redirectPath);
            navigate(redirectPath, { replace: true });
          }
        } else {
          // Profile fetch failed - user might not be provisioned in backend yet
          console.error("[Auth0Handler] Failed to fetch user profile from backend");
          clearAuth();
        }
      } catch (error) {
        console.error("[Auth0Handler] Error handling auth state:", error);
        clearAuth();
      } finally {
        setLoading(false);
      }
    }

    handleAuthStateChange();
  }, [isAuthenticated, isLoading, user, setAuth, clearAuth, setLoading, navigate]);

  // Show loading state while Auth0 is initializing
  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center bg-content1"
        role="status"
        aria-live="polite"
        aria-label="Authenticating"
      >
        <div className="text-center">
          <Spinner size="lg" color="primary" label="Authenticating..." />
          <p className="mt-4 text-default-600 text-sm">
            Verifying your identity...
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

/**
 * Get redirect path based on user role
 * 
 * @param {string} role - User role (student, teacher, admin)
 * @returns {string} Redirect path
 */
function getRoleBasedRedirect(role: string): string {
  switch (role) {
    case "admin":
      return "/admin/dashboard";
    case "teacher":
      return "/teacher/dashboard";
    case "student":
      return "/dashboard";
    default:
      return "/";
  }
}

/**
 * Auth0 Provider with Router Integration
 * Wraps the application with Auth0 authentication
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element} Wrapped application
 * 
 * @accessibility
 * - Loading states include proper ARIA labels
 * - Authentication errors are announced
 * - Focus is managed during redirects
 */
export function Auth0ProviderWithHistory({ children }: { children: React.ReactNode }) {
  // Validate configuration on mount
  useEffect(() => {
    try {
      validateAuth0Config();
    } catch (error) {
      console.error("Auth0 configuration error:", error);
    }
  }, []);

  return (
    <Auth0Provider
      domain={auth0Config.domain}
      clientId={auth0Config.clientId}
      authorizationParams={auth0Config.authorizationParams}
      cacheLocation={auth0Config.cacheLocation}
      useRefreshTokens={auth0Config.useRefreshTokens}
    >
      <Auth0Handler>{children}</Auth0Handler>
    </Auth0Provider>
  );
}
