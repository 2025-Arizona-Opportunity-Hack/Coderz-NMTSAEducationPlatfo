import type { Profile } from "../types/api";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  profile: Profile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (profile: Profile) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      profile: null,
      isAuthenticated: false,
      isLoading: true,
      setAuth: (profile) =>
        set({ profile, isAuthenticated: true, isLoading: false }),
      clearAuth: () =>
        set({ profile: null, isAuthenticated: false, isLoading: false }),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        profile: state.profile,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
