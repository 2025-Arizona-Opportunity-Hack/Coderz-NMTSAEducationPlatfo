import { useEffect } from "react";

import { authService } from "../services/auth.service";
import { useAuthStore } from "../store/useAuthStore";

export function useAuth() {
  const { setAuth, clearAuth, setLoading } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("auth-token");

        if (token) {
          // Verify token and get current user
          const profile = await authService.getCurrentUser();

          if (profile) {
            setAuth(profile);
          } else {
            // Token invalid, clear it
            localStorage.removeItem("auth-token");
            clearAuth();
          }
        } else {
          clearAuth();
        }
      } catch (error) {
        console.error("Auth initialization error:", error);
        localStorage.removeItem("auth-token");
        clearAuth();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [setAuth, clearAuth, setLoading]);
}
