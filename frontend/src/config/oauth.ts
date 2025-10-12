/**
 * OAuth Configuration
 * @deprecated Auth0 now handles all OAuth providers (Google, Microsoft, Apple, Facebook)
 * This file is kept for backwards compatibility but should not be used in new code
 * Use auth0.ts instead
 */

export type OAuthProvider =
  | "google"
  | "microsoft"
  | "apple"
  | "facebook"
  | "auth0";
