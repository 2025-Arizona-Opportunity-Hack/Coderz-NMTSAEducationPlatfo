/**
 * Main Application Router
 * 
 * Defines all application routes with proper authentication and role-based access control.
 * Implements lazy loading for code splitting and better performance.
 * 
 * @module App
 */

import { lazy, Suspense } from "react";
import { Routes, Route, } from "react-router-dom"
import { Spinner } from "@heroui/spinner";

import { useAuth } from "./hooks/useAuth";
import { Layout } from "./components/layout/Layout";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";

// Public pages - loaded immediately
import { Home } from "./pages/Home";
import { Explore } from "./pages/Explore";
import { CourseDetail } from "./pages/courses/CourseDetail";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { ForgotPassword } from "./pages/ForgotPassword";
import { Terms } from "./pages/Terms";
import { Privacy } from "./pages/Privacy";
import { AccessibilityStatement } from "./pages/AccessibilityStatement";
import { NotFound } from "./pages/NotFound";

// Student pages - lazy loaded
const Lesson = lazy(() => import("./pages/Lesson").then(m => ({ default: m.Lesson })));
const Dashboard = lazy(() => import("./pages/Dashboard").then(m => ({ default: m.Dashboard })));
const Applications = lazy(() => import("./pages/Applications").then(m => ({ default: m.Applications })));
const Forum = lazy(() => import("./pages/Forum").then(m => ({ default: m.Forum })));

// Teacher pages - lazy loaded (to be created)
// Placeholder imports - these files will be created
// const TeacherDashboard = lazy(() => import("./pages/teacher/TeacherDashboard"));
// const CreateCourse = lazy(() => import("./pages/teacher/CreateCourse"));
// const EditCourse = lazy(() => import("./pages/teacher/EditCourse"));

// Admin pages - lazy loaded (to be created)
// Placeholder imports - these files will be created
// const AdminDashboard = lazy(() => import("./pages/admin/AdminDashboard"));
// const UserManagement = lazy(() => import("./pages/admin/UserManagement"));
// const TeacherApplications = lazy(() => import("./pages/admin/TeacherApplications"));

/**
 * Loading fallback component for lazy-loaded routes
 * Provides accessible loading state with spinner
 */
function RouteLoadingFallback() {
  return (
    <div 
      className="min-h-screen flex items-center justify-center"
      role="status"
      aria-live="polite"
      aria-label="Loading page content"
    >
      <Spinner 
        size="lg" 
        color="primary"
        label="Loading..."
      />
    </div>
  );
}

/**
 * Main Application Component
 * Sets up routing structure with authentication checks
 * 
 * @returns {JSX.Element} Application router
 * 
 * @accessibility
 * - All routes include proper page titles via Helmet
 * - Loading states include ARIA labels
 * - Focus management handled by route transitions
 * - Skip links available on all pages
 */
function App() {
  // Initialize authentication state
  useAuth();

  return (
    <Suspense fallback={<RouteLoadingFallback />}>
      <Routes>
        <Route element={<Layout />} path="/">
          {/* ============================================================
              Public Routes - No Authentication Required
              ============================================================ */}
          
          <Route index element={<Home />} />
          <Route element={<Explore />} path="explore" />
          <Route element={<CourseDetail />} path="courses/:id" />
          <Route element={<Login />} path="login" />
          
          {/* Register and Forgot Password redirect to Login (Auth0 handles these) */}
          <Route element={<Register />} path="register" />
          <Route element={<ForgotPassword />} path="forgot-password" />
          
          {/* Legal pages */}
          <Route element={<Terms />} path="terms" />
          <Route element={<Privacy />} path="privacy" />
          <Route element={<AccessibilityStatement />} path="accessibility" />

          {/* ============================================================
              Student Routes - Authentication Required
              ============================================================ */}
          
          <Route
            element={
              <ProtectedRoute requiredRole="student">
                <Lesson />
              </ProtectedRoute>
            }
            path="courses/:courseId/lessons/:lessonId"
          />
          <Route
            element={
              <ProtectedRoute requiredRole="student">
                <Dashboard />
              </ProtectedRoute>
            }
            path="dashboard"
          />
          <Route
            element={
              <ProtectedRoute requiredRole="student">
                <Applications />
              </ProtectedRoute>
            }
            path="applications"
          />
          <Route
            element={
              <ProtectedRoute>
                <Forum />
              </ProtectedRoute>
            }
            path="forum"
          />

          {/* ============================================================
              Teacher Routes - Teacher Role Required
              ============================================================ */}
          
          {/* Teacher Dashboard will be implemented in Phase 2 */}
          {/* Uncomment when teacher pages are created:
          
          <Route
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherDashboard />
              </ProtectedRoute>
            }
            path="teacher/dashboard"
          />
          <Route
            element={
              <ProtectedRoute requiredRole="teacher">
                <CreateCourse />
              </ProtectedRoute>
            }
            path="teacher/courses/create"
          />
          <Route
            element={
              <ProtectedRoute requiredRole="teacher">
                <EditCourse />
              </ProtectedRoute>
            }
            path="teacher/courses/:id/edit"
          />
          
          */}

          {/* ============================================================
              Admin Routes - Admin Role Required
              ============================================================ */}
          
          {/* Admin Dashboard will be implemented in Phase 3 */}
          {/* Uncomment when admin pages are created:
          
          <Route
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
            path="admin/dashboard"
          />
          <Route
            element={
              <ProtectedRoute requiredRole="admin">
                <UserManagement />
              </ProtectedRoute>
            }
            path="admin/users"
          />
          <Route
            element={
              <ProtectedRoute requiredRole="admin">
                <TeacherApplications />
              </ProtectedRoute>
            }
            path="admin/applications"
          />
          
          */}

          {/* ============================================================
              Error Routes
              ============================================================ */}
          
          <Route element={<NotFound />} path="*" />
        </Route>
      </Routes>
    </Suspense>
  );
}

export default App;
