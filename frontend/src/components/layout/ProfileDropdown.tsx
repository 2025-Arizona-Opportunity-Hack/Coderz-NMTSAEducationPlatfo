import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { User, Settings, LogOut, ChevronDown } from "lucide-react";
import { useTranslation } from "react-i18next";

import { useAuthStore } from "../../store/useAuthStore";
import { authService } from "../../services/auth.service";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function ProfileDropdown() {
  const { t } = useTranslation();
  const { profile, clearAuth } = useAuthStore();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Get profile picture and name from stored profile
  const profilePicture = profile?.avatarUrl;
  const displayName = profile?.fullName || profile?.email || "User";

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handleLogout = async () => {
    try {
      await authService.signOut();
      clearAuth();
      // Redirect to Django logout endpoint
      // Django will clear session and logout from Auth0
      window.location.href = `${API_BASE_URL}/logout`;
    } catch {
      // Silent fail - still redirect to logout
      window.location.href = `${API_BASE_URL}/logout`;
    }
  };

  return (
    <div ref={dropdownRef} className="relative">
      <button
        aria-expanded={isOpen}
        aria-haspopup="true"
        className="flex items-center gap-2 p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
        onClick={() => setIsOpen(!isOpen)}
      >
        {profilePicture ? (
          <img
            alt={displayName}
            className="h-8 w-8 rounded-full object-cover"
            src={profilePicture}
          />
        ) : (
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-medium">
            {displayName.charAt(0).toUpperCase()}
          </div>
        )}
        <span className="hidden sm:block text-sm font-medium text-gray-700">
          {displayName}
        </span>
        <ChevronDown
          className={`h-4 w-4 text-gray-500 transition-transform ${isOpen ? "rotate-180" : ""}`}
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
          <div className="px-4 py-3 border-b border-gray-100">
            <p className="text-sm font-medium text-gray-900">{displayName}</p>
            <p className="text-xs text-gray-500 truncate">{profile?.email}</p>
          </div>

          <Link
            className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            to="/dashboard"
            onClick={() => setIsOpen(false)}
          >
            <User className="h-4 w-4" />
            {t("nav.myLearning")}
          </Link>

          <Link
            className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            to="/settings"
            onClick={() => setIsOpen(false)}
          >
            <Settings className="h-4 w-4" />
            {t("nav.settings")}
          </Link>

          <div className="border-t border-gray-100 mt-1 pt-1">
            <button
              className="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4" />
              {t("nav.logout")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
