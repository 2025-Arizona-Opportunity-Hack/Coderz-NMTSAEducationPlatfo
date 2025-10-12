import type { Profile, ApiError } from "../types/api";
import type { OAuthProvider } from "../config/oauth";

import api from "../config/api";

export interface OAuthSignInData {
  provider: OAuthProvider;
  email: string;
  name: string;
  picture?: string;
}

export interface Auth0SignInData {
  auth0Token: string;
  email: string;
  name: string;
  picture?: string;
}

export interface OAuthSignInResponse {
  token: string;
  refreshToken: string;
  user: Profile;
  profile: Profile; // Alias for compatibility
  isNewUser: boolean;
}

export interface RoleSelectionData {
  role: "student" | "teacher";
}

export interface TeacherOnboardingData {
  bio?: string;
  credentials?: string;
  specialization?: string;
  years_experience?: number;
  resume?: File;
  certifications?: File;
}

export interface StudentOnboardingData {
  relationship?: string;
  care_recipient_name?: string;
  care_recipient_age?: number;
  special_needs?: string;
  learning_goals?: string;
  interests?: string;
  accessibility_needs?: string;
}

export const authService = {
  /**
   * Auth0 Sign In - Exchange Auth0 token with backend
   * Frontend uses Auth0 for authentication, backend validates token and returns JWT
   * Returns isNewUser flag to determine if onboarding is needed
   */
  async auth0SignIn(data: Auth0SignInData): Promise<OAuthSignInResponse> {
    try {
      const response = await api.post<OAuthSignInResponse>(
        "/auth/oauth/signin",
        {
          provider: "auth0",
          ...data,
        },
      );
      const { token, user, isNewUser } = response.data;

      // Store token
      localStorage.setItem("auth-token", token);

      return { ...response.data, profile: user, token, isNewUser };
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to sign in with Auth0");
    }
  },

  /**
   * OAuth Sign In - Send user data from OAuth provider to backend
   * Frontend handles OAuth, backend just creates/updates user and returns JWT
   * Returns isNewUser flag to determine if onboarding is needed
   * @deprecated Use auth0SignIn instead
   */
  async oauthSignIn(data: OAuthSignInData): Promise<OAuthSignInResponse> {
    try {
      const response = await api.post<OAuthSignInResponse>(
        "/auth/oauth/signin",
        data,
      );
      const { token, user, isNewUser } = response.data;

      // Store token
      localStorage.setItem("auth-token", token);

      return { ...response.data, profile: user, token, isNewUser };
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to sign in with OAuth");
    }
  },

  /**
   * Select user role during onboarding
   */
  async selectRole(data: RoleSelectionData) {
    try {
      const response = await api.post("/onboarding/select-role", data);

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to select role");
    }
  },

  /**
   * Complete teacher onboarding
   */
  async completeTeacherOnboarding(data: TeacherOnboardingData) {
    try {
      const formData = new FormData();

      if (data.bio) formData.append("bio", data.bio);
      if (data.credentials) formData.append("credentials", data.credentials);
      if (data.specialization)
        formData.append("specialization", data.specialization);
      if (data.years_experience !== undefined) {
        formData.append("years_experience", data.years_experience.toString());
      }
      if (data.resume) formData.append("resume", data.resume);
      if (data.certifications)
        formData.append("certifications", data.certifications);

      const response = await api.post("/onboarding/teacher", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(
        apiError.message || "Failed to complete teacher onboarding",
      );
    }
  },

  /**
   * Complete student onboarding
   */
  async completeStudentOnboarding(data: StudentOnboardingData) {
    try {
      const response = await api.post("/onboarding/student", data);

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(
        apiError.message || "Failed to complete student onboarding",
      );
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
