/**
 * Register Page - Redirects to Auth0
 * 
 * Since Auth0 handles both registration and login through Universal Login,
 * this page redirects to the login page.
 */

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function Register() {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to login - Auth0 Universal Login handles registration
    navigate("/login", { replace: true });
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-default-600">Redirecting to sign in...</p>
    </div>
  );
}
