/**
 * Auth0 Configuration
 * Auth0 handles all OAuth providers: Google, Microsoft, Apple, Facebook
 * Configure providers in Auth0 Dashboard -> Authentication -> Social
 *
 * Note: Client Secret is NOT needed for frontend SPAs - it's only for backend/confidential clients
 */

// Build the full callback URL
const baseUrl = import.meta.env.VITE_APP_URL || "http://localhost:5173";
const redirectUri = `${baseUrl}/callback`;

// Debug logging - shows what redirect_uri will be sent to Auth0
// This MUST match EXACTLY what's configured in Auth0 dashboard
/* eslint-disable no-console */
console.log("🔐 Auth0 Configuration:");
console.log("  Domain:", import.meta.env.VITE_AUTH0_DOMAIN);
console.log("  Client ID:", import.meta.env.VITE_AUTH0_CLIENT_ID);
console.log("  Redirect URI:", redirectUri);
console.log(
  "⚠️  Make sure this URL is in Auth0 Dashboard > Application > Allowed Callback URLs",
);
/* eslint-enable no-console */

export const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN || "",
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID || "",
  authorizationParams: {
    redirect_uri: redirectUri,
    // Audience is optional - only needed if calling a protected API
    ...(import.meta.env.VITE_AUTH0_AUDIENCE && {
      audience: import.meta.env.VITE_AUTH0_AUDIENCE,
    }),
    scope: "openid profile email",
  },
  cacheLocation: "localstorage" as const,
  useRefreshTokens: true,
};
