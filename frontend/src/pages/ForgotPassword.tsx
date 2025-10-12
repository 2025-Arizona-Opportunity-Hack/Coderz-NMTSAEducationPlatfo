/**
 * Forgot Password Page - Redirects to Auth0
 * 
 * Password reset is handled by Auth0 Universal Login.
 * Redirects users to the login page where they can use "Forgot Password".
 */

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function ForgotPassword() {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to login - Auth0 handles password reset
    navigate("/login", { replace: true });
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-default-600">Redirecting to sign in...</p>
    </div>
  );
}
