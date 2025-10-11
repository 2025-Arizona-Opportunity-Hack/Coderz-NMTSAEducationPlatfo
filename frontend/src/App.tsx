import { Routes, Route } from "react-router-dom";

import { useAuth } from "./hooks/useAuth";
import { Layout } from "./components/layout/Layout";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";
import { Home } from "./pages/Home";
import { Explore } from "./pages/Explore";
import { CourseDetail } from "./pages/courses/CourseDetail";
import { Lesson } from "./pages/Lesson";
import { Dashboard } from "./pages/Dashboard";
import { Forum } from "./pages/Forum";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { ForgotPassword } from "./pages/ForgotPassword";

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
              <Forum />
            </ProtectedRoute>
          }
          path="forum"
        />
        <Route element={<Login />} path="login" />
        <Route element={<Register />} path="register" />
        <Route element={<ForgotPassword />} path="forgot-password" />
      </Route>
    </Routes>
  );
}

export default App;
