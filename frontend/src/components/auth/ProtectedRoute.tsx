import { Navigate, useLocation } from "react-router-dom";

import { useAuthStore } from "../../store/useAuthStore";

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: Array<"student" | "instructor" | "admin">;
}

export function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const { isAuthenticated, profile, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div
            className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"
            role="status"
          >
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  if (allowedRoles && profile && !allowedRoles.includes(profile.role)) {
    return <Navigate replace to="/" />;
  }

  return <>{children}</>;
}
