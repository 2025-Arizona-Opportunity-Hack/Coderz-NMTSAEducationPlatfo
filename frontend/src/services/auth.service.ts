import type { Profile, AuthResponse, ApiError } from "../types/api";

import api from "../config/api";

export interface SignUpData {
  email: string;
  password: string;
  fullName: string;
  role?: "student" | "instructor";
}

export interface SignInData {
  email: string;
  password: string;
}

export interface AdminSignInData {
  username: string;
  password: string;
}

export const authService = {
  async signUp(data: SignUpData) {
    try {
      const response = await api.post<AuthResponse>("/auth/register", data);
      const { token, user } = response.data;

      // Store token
      localStorage.setItem("auth-token", token);

      return { user, token };
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to sign up");
    }
  },

  async signIn(data: SignInData) {
    try {
      const response = await api.post<AuthResponse>("/auth/login", data);
      const { token, user } = response.data;

      // Store token
      localStorage.setItem("auth-token", token);

      return { profile: user, token };
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to sign in");
    }
  },

  async adminSignIn(data: AdminSignInData) {
    try {
      const response = await api.post<AuthResponse>("/auth/admin/login", data);
      const { token, user } = response.data;

      // Store token
      localStorage.setItem("auth-token", token);

      return { profile: user, token };
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to sign in");
    }
  },

  async signOut() {
    try {
      await api.post("/auth/logout");
      localStorage.removeItem("auth-token");
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to sign out");
    }
  },

  async getProfile(userId: string): Promise<Profile | null> {
    try {
      const response = await api.get<Profile>(`/users/${userId}`);

      return response.data;
    } catch {
      return null;
    }
  },

  async getCurrentUser(): Promise<Profile | null> {
    try {
      const response = await api.get<Profile>("/auth/me");

      return response.data;
    } catch {
      return null;
    }
  },
};
