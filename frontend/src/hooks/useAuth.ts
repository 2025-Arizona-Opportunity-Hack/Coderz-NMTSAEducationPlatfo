/**
 * useAuth Hook
 * 
 * This hook is now a no-op since Auth0ProviderWithHistory handles
 * all authentication state management.
 * 
 * Kept for backward compatibility with existing code.
 */
export function useAuth() {
  // Auth0ProviderWithHistory now handles all auth state
  // This hook is kept for backward compatibility but does nothing
  return;
}
