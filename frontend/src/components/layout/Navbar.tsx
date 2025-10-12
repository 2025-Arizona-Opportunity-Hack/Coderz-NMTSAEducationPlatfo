import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Menu, BookOpen } from "lucide-react";
import { useState } from "react";

import { useAuthStore } from "../../store/useAuthStore";
import { ProfileDropdown } from "./ProfileDropdown";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function Navbar() {
  const { t, i18n } = useTranslation();
  const { isAuthenticated } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isLoggedIn = isAuthenticated;

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === "en" ? "es" : "en");
  };

  const handleLogin = () => {
    // Redirect to Django backend login endpoint
    // Backend will handle Auth0 OAuth flow
    window.location.href = `${API_BASE_URL}/login`;
  };

  return (
    <nav
      aria-label="Main navigation"
      className="bg-white shadow-sm border-b border-gray-200"
      role="navigation"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-8">
            <Link
              aria-label="NMTSA Learn home"
              className="flex items-center gap-2 text-xl font-bold text-gray-900 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-2"
              to="/"
            >
              <BookOpen aria-hidden="true" className="h-6 w-6" />
              <span>NMTSA Learn</span>
            </Link>

            <div className="hidden md:flex items-center gap-6">
              <Link
                className="text-gray-700 hover:text-blue-600 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-2 py-1"
                to="/explore"
              >
                {t("nav.explore")}
              </Link>
              {isLoggedIn && (
                <>
                  <Link
                    className="text-gray-700 hover:text-blue-600 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-2 py-1"
                    to="/dashboard"
                  >
                    {t("nav.myLearning")}
                  </Link>
                  <Link
                    className="text-gray-700 hover:text-blue-600 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-2 py-1"
                    to="/applications"
                  >
                    {t("nav.applications")}
                  </Link>
                  <Link
                    className="text-gray-700 hover:text-blue-600 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-2 py-1"
                    to="/forum"
                  >
                    {t("nav.forum")}
                  </Link>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              aria-label={`Switch to ${i18n.language === "en" ? "Spanish" : "English"}`}
              className="p-2 text-gray-700 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
              onClick={toggleLanguage}
            >
              <span className="ml-1 text-sm font-medium">
                {i18n.language.toUpperCase()}
              </span>
            </button>

            <div className="hidden md:flex items-center gap-3">
              {isLoggedIn ? (
                <ProfileDropdown />
              ) : (
                <button
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
                  onClick={handleLogin}
                >
                  {t("nav.login")}
                </button>
              )}
            </div>

            <button
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle mobile menu"
              className="md:hidden p-2 text-gray-700 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <Menu aria-hidden="true" className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div
          className="md:hidden border-t border-gray-200 bg-white"
          role="menu"
        >
          <div className="px-4 py-3 space-y-2">
            <Link
              className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              role="menuitem"
              to="/explore"
            >
              {t("nav.explore")}
            </Link>
            {isLoggedIn && (
              <>
                <Link
                  className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  role="menuitem"
                  to="/dashboard"
                >
                  {t("nav.myLearning")}
                </Link>
                <Link
                  className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  role="menuitem"
                  to="/applications"
                >
                  {t("nav.applications")}
                </Link>
                <Link
                  className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  role="menuitem"
                  to="/forum"
                >
                  {t("nav.forum")}
                </Link>
              </>
            )}
            {isLoggedIn ? (
              <div className="px-3 py-2">
                <ProfileDropdown />
              </div>
            ) : (
              <button
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                role="menuitem"
                onClick={handleLogin}
              >
                {t("nav.login")}
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
