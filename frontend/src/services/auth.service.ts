/**
 * Authentication Service
 * 
 * Handles user authentication via Auth0 OAuth only.
 * All authentication flows go through Auth0 - no local email/password.
 * Works with Django backend that validates Auth0 JWT tokens.
 * 
 * @module services/auth
 */

import type { Profile } from "../types/api";

import api from "../config/api";

/**
 * Auth0 logout handler
 * Will be set by the Auth0Provider wrapper
 */
let auth0LogoutFn: (() => void) | null = null;

/**
 * Set the Auth0 logout function
 * Called by Auth0Provider during initialization
 * 
 * @param {Function} fn - Function that triggers Auth0 logout
 */
export function setAuth0Logout(fn: () => void): void {
  auth0LogoutFn = fn;
}

/**
 * Authentication Service
 * Provides methods for Auth0-based authentication and profile management
 * 
 * @note All sign-in/sign-up flows go through Auth0. Local email/password is not supported.
 */
export const authService = {
  /**
   * Initiate Auth0 login
   * Redirects user to Auth0 Universal Login
   * 
   * @throws {Error} Auth0 is not configured or unavailable
   * 
   * @accessibility
   * - Login page should be keyboard accessible
   * - Screen readers should announce redirect
   */
  async login(): Promise<void> {
    throw new Error(
      "Please use Auth0Provider's loginWithRedirect method. " +
      "This method is deprecated in OAuth-only mode."
    );
  },

  /**
   * Sign out current user via Auth0
   * Clears Auth0 session and local application state
   * 
   * @returns {Promise<void>}
   * 
   * @accessibility
   * - Logout action should be announced to screen readers
   */
  async signOut(): Promise<void> {
    try {
      // Clear local storage
      localStorage.removeItem("auth-storage");
      
      // Trigger Auth0 logout if available
      if (auth0LogoutFn) {
        auth0LogoutFn();
      } else {
        // Fallback: redirect to home
        window.location.href = "/";
      }
    } catch (error) {
      console.error("Logout error:", error);
      // Always redirect even if logout fails
      window.location.href = "/";
    }
  },

  /**
   * Get current authenticated user profile from backend
   * Backend validates Auth0 token and returns user data with roles
   * 
   * @returns {Promise<Profile | null>} Current user profile or null if not authenticated
   * 
   * @accessibility
   * - Profile data should be cached to reduce API calls
   * - Should handle session expiry gracefully
   */
  async getCurrentUser(): Promise<Profile | null> {
    try {
      const response = await api.get<Profile>("/auth/me/");
      return response.data;
    } catch (error) {
      console.error("Failed to get current user:", error);
      return null;
    }
  },

  /**
   * Get Auth0 access token
   * This method is deprecated - use Auth0Provider's getAccessTokenSilently instead
   * 
   * @deprecated Use Auth0Provider context
   * @throws {Error} Always throws in OAuth-only mode
   */
  async getAccessToken(): Promise<string> {
    throw new Error(
      "Use Auth0Provider's getAccessTokenSilently method instead. " +
      "Local token management is not supported in OAuth-only mode."
    );
  },
};
