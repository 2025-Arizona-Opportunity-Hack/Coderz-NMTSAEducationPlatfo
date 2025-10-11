import { Routes, Route } from "react-router-dom";

import { useAuth } from "./hooks/useAuth";
import { Layout } from "./components/layout/Layout";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";
import { Home } from "./pages/Home";
import { Explore } from "./pages/Explore";
import { CourseDetail } from "./pages/courses/CourseDetail";
import { Lesson } from "./pages/Lesson";
import { Dashboard } from "./pages/Dashboard";
import { Applications } from "./pages/Applications";
import { Forum } from "./pages/Forum";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Terms } from "./pages/Terms";
import { Privacy } from "./pages/Privacy";
import { AccessibilityStatement } from "./pages/AccessibilityStatement";
import { NotFound } from "./pages/NotFound";
import AdminLogin from "./pages/AdminLogin";

function App() {
  useAuth();

  return (
    <Routes>
      <Route element={<Layout />} path="/">
        <Route index element={<Home />} />
        <Route element={<Explore />} path="explore" />
        <Route element={<CourseDetail />} path="courses/:id" />
        <Route
          element={
            <ProtectedRoute>
              <Lesson />
            </ProtectedRoute>
          }
          path="courses/:courseId/lessons/:lessonId"
        />
        <Route
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
          path="dashboard"
        />
        <Route
          element={
            <ProtectedRoute>
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
        <Route element={<AdminLogin />} path="admin/login" />
        <Route element={<Login />} path="login" />
        <Route element={<Register />} path="register" />
        <Route element={<Terms />} path="terms" />
        <Route element={<Privacy />} path="privacy" />
        <Route element={<AccessibilityStatement />} path="accessibility" />
        <Route element={<NotFound />} path="*" />
      </Route>
    </Routes>
  );
}

export default App;
