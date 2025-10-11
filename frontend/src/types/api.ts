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

export interface Lesson {
  id: string;
  moduleId: string;
  title: string;
  description: string;
  type: "video" | "reading" | "quiz" | "assignment";
  duration: number; // in minutes
  order: number;
  isCompleted?: boolean;
  isLocked?: boolean;
  contentUrl?: string;
}

export interface Module {
  id: string;
  courseId: string;
  title: string;
  description: string;
  order: number;
  lessons: Lesson[];
  isCompleted?: boolean;
}

export interface Review {
  id: string;
  courseId: string;
  userId: string;
  user: {
    id: string;
    fullName: string;
    avatarUrl?: string;
  };
  rating: number; // 1-5
  comment: string;
  createdAt: string;
  updatedAt: string;
}

export interface CourseDetail extends Course {
  longDescription?: string;
  prerequisites?: string[];
  learningObjectives?: string[];
  instructor: {
    id: string;
    fullName: string;
    avatarUrl?: string;
    bio?: string;
    credentials?: string;
    socialLinks?: {
      linkedin?: string;
      twitter?: string;
      website?: string;
    };
  };
  modules?: Module[];
  reviews?: Review[];
  averageRating?: number;
  totalReviews?: number;
  isEnrolled?: boolean;
  progress?: number; // 0-100, enrollment progress percentage
}

export interface Resource {
  id: string;
  lessonId: string;
  title: string;
  type: string; // e.g., "pdf", "docx", "zip"
  fileUrl: string;
  fileSize?: number; // in bytes
}

export interface LessonContent extends Lesson {
  content: string; // markdown or video URL
  videoUrl?: string;
  captions?: Array<{
    src: string;
    srclang?: string;
    label?: string;
    isDefault?: boolean;
  }>;
  resources?: Resource[];
  nextLesson?: {
    id: string;
    title: string;
  };
  previousLesson?: {
    id: string;
    title: string;
  };
}

export interface Note {
  id: string;
  lessonId: string;
  userId: string;
  content: string;
  timestamp?: number; // video timestamp in seconds
  createdAt: string;
  updatedAt: string;
}

export interface LessonProgress {
  lessonId: string;
  courseId: string;
  isCompleted: boolean;
  timeSpent: number; // in seconds
  lastPosition?: number; // video position in seconds
  completedAt?: string;
}
