/**
 * API Types for NMTSA Learn Backend
 * 
 * This module defines TypeScript interfaces that match the Django backend API
 * response formats. Key considerations:
 * - Django uses snake_case, but we use camelCase in frontend
 * - Transform functions handle conversion between formats
 * - All types follow WCAG 2.1 accessibility requirements where applicable
 * 
 * @module types/api
 */

// ============================================================================
// Django-Specific Response Types
// ============================================================================

/**
 * Django REST Framework pagination response wrapper
 * Used for all list endpoints that return paginated data
 */
export interface DjangoPaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Standard Django error response format
 * Includes validation errors in field-specific format
 */
export interface DjangoErrorResponse {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
  [key: string]: any;
}

// ============================================================================
// Authentication & User Types
// ============================================================================

/**
 * User profile information
 * Maps to Django CustomUser model
 */
export interface Profile {
  id: string;
  email: string;
  fullName: string;
  role: "student" | "teacher" | "admin";
  avatarUrl?: string;
  bio?: string;
  createdAt: string;
  updatedAt: string;
  // Django-specific fields
  username?: string;
  firstName?: string;
  lastName?: string;
  isActive?: boolean;
  dateJoined?: string;
}

/**
 * Authentication response from login/register endpoints
 * Includes JWT access and refresh tokens
 */
export interface AuthResponse {
  user: Profile;
  token: string; // JWT access token
  access?: string; // Alternative format from Django
  refreshToken?: string;
  refresh?: string; // Alternative format from Django
  tokenType?: string; // Usually "Bearer"
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

// ============================================================================
// Course & Learning Types
// ============================================================================

/**
 * Course information
 * Maps to Django Course model
 */
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
  duration: number; // in minutes (duration_minutes in Django)
  credits: number;
  rating?: number; // average_rating in Django
  enrollmentCount?: number; // enrollment_count in Django
  createdAt: string;
  updatedAt: string;
  // Django-specific fields
  isPublished?: boolean;
  prerequisites?: string | string[]; // Can be string or array
  learningObjectives?: string[];
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

export interface EnrollmentWithProgress extends Enrollment {
  course: Course;
  lastAccessedAt?: string;
  currentLesson?: {
    id: string;
    title: string;
    moduleTitle: string;
  };
}

export interface Certificate {
  id: string;
  courseId: string;
  userId: string;
  course: {
    id: string;
    title: string;
    instructor: string;
  };
  completedAt: string;
  certificateUrl: string;
}

export interface DashboardStats {
  totalCourses: number;
  inProgressCourses: number;
  completedCourses: number;
  totalCertificates: number;
  totalLearningHours: number;
  currentStreak: number; // days
  longestStreak: number; // days
}

export interface ContinueLearningItem {
  enrollment: EnrollmentWithProgress;
  nextLesson: {
    id: string;
    title: string;
    type: "video" | "reading" | "quiz" | "assignment";
    duration: number;
  };
}

/**
 * Course application status
 * Matches Django ApplicationStatus choices
 */
export type ApplicationStatus =
  | "pending"
  | "under_review"
  | "approved"
  | "rejected"
  | "cancelled";

/**
 * Course application
 * Used for teacher verification applications
 */
export interface Application {
  id: string;
  userId: string;
  courseId: string;
  status: ApplicationStatus;
  motivationStatement: string;
  prerequisitesConfirmed: boolean;
  submittedAt: string;
  reviewedAt?: string;
  reviewedBy?: string;
  reviewFeedback?: string;
  documents?: {
    id: string;
    name: string;
    url: string;
    uploadedAt: string;
  }[];
  course: {
    id: string;
    title: string;
    thumbnailUrl?: string;
    instructor: {
      id: string;
      fullName: string;
      avatarUrl?: string;
    };
  };
}

export interface CreateApplicationDto {
  courseId: string;
  motivationStatement: string;
  prerequisitesConfirmed: boolean;
  documents?: File[];
}

export interface ForumPost {
  id: string;
  title: string;
  content: string;
  excerpt: string;
  authorId: string;
  author: {
    id: string;
    fullName: string;
    avatarUrl?: string;
    role: "student" | "instructor" | "admin";
  };
  tags: string[];
  likes: number;
  commentsCount: number;
  isLiked: boolean;
  isPinned: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ForumComment {
  id: string;
  postId: string;
  content: string;
  authorId: string;
  author: {
    id: string;
    fullName: string;
    avatarUrl?: string;
    role: "student" | "instructor" | "admin";
  };
  parentId?: string;
  replies?: ForumComment[];
  likes: number;
  isLiked: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreatePostDto {
  title: string;
  content: string;
  tags: string[];
}

export interface UpdatePostDto {
  title?: string;
  content?: string;
  tags?: string[];
}

export interface CreateCommentDto {
  postId: string;
  content: string;
  parentId?: string;
}
