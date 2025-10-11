// API Types for NMTSA Learn Backend

export interface Profile {
  id: string;
  email: string;
  fullName: string;
  role: "student" | "instructor" | "admin";
  avatarUrl?: string;
  bio?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  user: Profile;
  token: string;
  refreshToken?: string;
}

export interface ApiError {
  message: string;
  statusCode?: number;
  errors?: Record<string, string[]>;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface Course {
  id: string;
  title: string;
  description: string;
  thumbnailUrl?: string;
  instructorId: string;
  instructor?: {
    id: string;
    fullName: string;
    avatarUrl?: string;
  };
  category: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  duration: number; // in minutes
  credits: number;
  rating?: number;
  enrollmentCount?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Enrollment {
  id: string;
  userId: string;
  courseId: string;
  progress: number; // 0-100
  completedLessons: string[];
  enrolledAt: string;
  completedAt?: string;
}
