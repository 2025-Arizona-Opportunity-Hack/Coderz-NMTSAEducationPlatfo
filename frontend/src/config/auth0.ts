/**
 * Auth0 Configuration
 * 
 * Provides Auth0 settings for SPA authentication with PKCE flow.
 * All authentication goes through Auth0 - no local email/password.
 * 
 * @module config/auth0
 */

/**
 * Auth0 configuration object
 * Values are loaded from environment variables
 */
export const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN || "",
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID || "",
  authorizationParams: {
    redirect_uri: import.meta.env.VITE_AUTH0_REDIRECT_URI || window.location.origin,
    audience: import.meta.env.VITE_AUTH0_AUDIENCE || "",
    scope: import.meta.env.VITE_AUTH0_SCOPE || "openid profile email",
  },
  // Use in-memory token storage for security
  cacheLocation: "memory" as const,
  // Use refresh tokens for silent authentication
  useRefreshTokens: true,
};

/**
 * Validate Auth0 configuration
 * Throws error if required config is missing
 */
export function validateAuth0Config(): void {
  const required = [
    { key: "VITE_AUTH0_DOMAIN", value: auth0Config.domain },
    { key: "VITE_AUTH0_CLIENT_ID", value: auth0Config.clientId },
    { key: "VITE_AUTH0_AUDIENCE", value: auth0Config.authorizationParams.audience },
  ];

  const missing = required.filter((config) => !config.value);

  if (missing.length > 0) {
    const missingKeys = missing.map((c) => c.key).join(", ");
    throw new Error(
      `Missing required Auth0 configuration: ${missingKeys}. ` +
      `Please check your .env file.`
    );
  }
}
