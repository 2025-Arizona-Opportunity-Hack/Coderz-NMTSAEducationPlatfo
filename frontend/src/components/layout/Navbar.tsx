import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Menu, Globe, BookOpen } from "lucide-react";
import { useState } from "react";

import { useAuthStore } from "../../store/useAuthStore";
import { authService } from "../../services/auth.service";

export function Navbar() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, clearAuth, profile } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === "en" ? "es" : "en");
  };

  const handleLogout = async () => {
    try {
      await authService.signOut();
      clearAuth();
      navigate("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
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
              {isAuthenticated && (
                <>
                  <Link
                    className="text-gray-700 hover:text-blue-600 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md px-2 py-1"
                    to="/dashboard"
                  >
                    {t("nav.myLearning")}
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
              <Globe aria-hidden="true" className="h-5 w-5" />
              <span className="ml-1 text-sm font-medium">
                {i18n.language.toUpperCase()}
              </span>
            </button>

            <div className="hidden md:flex items-center gap-3">
              {isAuthenticated ? (
                <>
                  {profile && (
                    <span className="text-sm text-gray-600">
                      {profile.full_name || profile.email}
                    </span>
                  )}
                  <button
                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
                    onClick={handleLogout}
                  >
                    {t("nav.logout")}
                  </button>
                </>
              ) : (
                <>
                  <Link
                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
                    to="/login"
                  >
                    {t("nav.login")}
                  </Link>
                  <Link
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    to="/register"
                  >
                    {t("nav.register")}
                  </Link>
                </>
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
            {isAuthenticated && (
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
                  to="/forum"
                >
                  {t("nav.forum")}
                </Link>
              </>
            )}
            {isAuthenticated ? (
              <button
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                role="menuitem"
                onClick={handleLogout}
              >
                {t("nav.logout")}
              </button>
            ) : (
              <>
                <Link
                  className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  role="menuitem"
                  to="/login"
                >
                  {t("nav.login")}
                </Link>
                <Link
                  className="block px-3 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-center"
                  role="menuitem"
                  to="/register"
                >
                  {t("nav.register")}
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
