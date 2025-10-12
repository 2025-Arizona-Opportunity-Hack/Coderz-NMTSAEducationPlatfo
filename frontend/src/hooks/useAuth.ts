import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

import { authService } from "../services/auth.service";
import { useAuthStore } from "../store/useAuthStore";

/**
 * Custom hook that checks authentication status with backend
 * For Regular Web Application, authentication is handled by Django backend
 * This hook is called once when the app loads (in App.tsx)
 * It handles:
 * 1. Checking if user has valid session with backend
 * 2. Loading user profile from backend
 * 3. Storing auth state in Zustand store
 * 4. Redirecting to onboarding for new users if needed
 */
export function useAuth() {
  const { setAuth, clearAuth, setLoading } = useAuthStore();
  const navigate = useNavigate();
  const hasCheckedAuth = useRef(false);

  useEffect(() => {
    const initAuth = async () => {
      // Only check once on mount
      if (hasCheckedAuth.current) {
        return;
      }

      hasCheckedAuth.current = true;

      try {
        setLoading(true);

        // Check if we have a valid backend token
        const token = localStorage.getItem("auth-token");

        if (token) {
          // Verify token and get current user from backend
          const profile = await authService.getCurrentUser();

          if (profile) {
            setAuth(profile);

            // Check if onboarding is needed
            if (!profile.role) {
              navigate("/onboarding", { replace: true });
            }

            return;
          }

          // Token invalid, clear it
          localStorage.removeItem("auth-token");
        }

        // No valid token, clear auth state
        clearAuth();
      } catch {
        // Silent fail - authentication will be retried
        localStorage.removeItem("auth-token");
        clearAuth();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [setAuth, clearAuth, setLoading, navigate]);
}
