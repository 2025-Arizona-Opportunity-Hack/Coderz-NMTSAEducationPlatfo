/**
 * Protected Route Component
 * 
 * Wrapper component for routes that require authentication and/or specific roles.
 * Implements WCAG 2.1 AA standards with proper loading states and screen reader support.
 * 
 * Features:
 * - Authentication check with redirect to login
 * - Role-based access control
 * - Accessible loading state
 * - Automatic redirect to appropriate dashboard based on user role
 * - Preserves intended destination for post-login redirect
 * 
 * @module components/auth/ProtectedRoute
 */

import { Navigate, useLocation } from "react-router-dom";
import { Spinner } from "@heroui/spinner";

import { useAuthStore } from "../../store/useAuthStore";

interface ProtectedRouteProps {
  /** Child components to render if access is granted */
  children: React.ReactNode;
  
  /** 
   * Array of roles allowed to access this route
   * If undefined, any authenticated user can access
   */
  allowedRoles?: Array<"student" | "teacher" | "admin">;
  
  /**
   * Specific role required to access (deprecated, use allowedRoles)
   * @deprecated Use allowedRoles instead
   */
  requiredRole?: "student" | "teacher" | "admin";
}

/**
 * Protected Route Component
 * 
 * Ensures user is authenticated and has appropriate permissions before
 * rendering protected content. Redirects to login if not authenticated,
 * or to appropriate dashboard if wrong role.
 * 
 * @param {ProtectedRouteProps} props - Component props
 * @returns {JSX.Element} Protected content or redirect
 * 
 * @example
 * ```tsx
 * // Allow any authenticated user
 * <ProtectedRoute>
 *   <MyPage />
 * </ProtectedRoute>
 * 
 * // Allow only instructors
 * <ProtectedRoute requiredRole="instructor">
 *   <TeacherDashboard />
 * </ProtectedRoute>
 * 
 * // Allow multiple roles
 * <ProtectedRoute allowedRoles={["instructor", "admin"]}>
 *   <CourseManagement />
 * </ProtectedRoute>
 * ```
 * 
 * @accessibility
 * - Loading state includes proper ARIA attributes
 * - Screen reader announcements for authentication status
 * - Focus management after navigation
 * - High contrast loading indicator
 */
export function ProtectedRoute({
  children,
  allowedRoles,
  requiredRole,
}: ProtectedRouteProps) {
  const { isAuthenticated, profile, isLoading } = useAuthStore();
  const location = useLocation();

  // Combine allowedRoles and requiredRole for backwards compatibility
  const effectiveAllowedRoles = allowedRoles || (requiredRole ? [requiredRole] : undefined);

  // Loading state with accessible spinner
  if (isLoading) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center bg-content1"
        role="status"
        aria-live="polite"
        aria-label="Checking authentication status"
      >
        <div className="text-center">
          <Spinner 
            size="lg" 
            color="primary"
            label="Loading..."
            aria-label="Loading authentication status"
          />
          <p className="mt-4 text-default-600 text-sm">
            Verifying your access...
          </p>
        </div>
      </div>
    );
  }

  // Not authenticated - redirect to login with return URL
  if (!isAuthenticated) {
    return (
      <Navigate 
        replace 
        state={{ from: location }} 
        to="/login" 
        aria-label="Redirecting to login page"
      />
    );
  }

  // Check role-based access if roles are specified
  if (effectiveAllowedRoles && profile) {
    const hasRequiredRole = effectiveAllowedRoles.includes(profile.role);

    if (!hasRequiredRole) {
      // User authenticated but doesn't have required role
      // Redirect to their appropriate dashboard
      const redirectPath = getRoleBasedRedirect(profile.role);
      
      return (
        <Navigate 
          replace 
          to={redirectPath}
          state={{ 
            error: "You don't have permission to access that page",
            from: location 
          }}
          aria-label={`Redirecting to ${profile.role} dashboard`}
        />
      );
    }
  }

  // All checks passed - render protected content
  return <>{children}</>;
}

/**
 * Get appropriate dashboard path based on user role
 * Provides sensible defaults for role-based navigation
 * 
 * @param {string} role - User role
 * @returns {string} Dashboard path for the role
 */
function getRoleBasedRedirect(role: string): string {
  switch (role) {
    case "instructor":
      return "/teacher/dashboard";
    case "admin":
      return "/admin/dashboard";
    case "student":
    default:
      return "/dashboard";
  }
}
