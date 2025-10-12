// API Types for NMTSA Learn Backend
// These types match the Django backend serializers exactly

export interface Profile {
  id: string;
  email: string;
  fullName: string;
  profilePicture?: string;
  role: "student" | "teacher" | "admin"; // Changed from "instructor" to "teacher"
  avatarUrl?: string;
  createdAt: string;
  updatedAt: string;
}

// Extended profile with role-specific data
export interface UserProfile {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: "student" | "teacher" | "admin";
  profile_picture?: string;
  onboarding_complete: boolean;
  is_active: boolean;
  date_joined: string;
  teacher_profile?: TeacherProfile;
  student_profile?: StudentProfile;
}

export interface TeacherProfile {
  bio: string;
  credentials: string;
  specialization: string;
  years_experience?: number;
  verification_status: "pending" | "approved" | "rejected";
  resume?: string;
  certifications?: string;
}

export interface StudentProfile {
  relationship: string;
  care_recipient_name: string;
  care_recipient_age?: number;
  special_needs: string;
  learning_goals: string;
  interests: string;
  accessibility_needs: string;
}

export interface AuthResponse {
  user: Profile;
  token: string;
  refreshToken?: string;
  isNewUser?: boolean; // Only present for OAuth signin
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

export interface Instructor {
  id: string;
  fullName: string;
  avatarUrl?: string;
  bio?: string;
  credentials?: string;
}

export interface Course {
  id: string;
  title: string;
  description: string;
  thumbnailUrl?: string;
  instructorId: string;
  instructor: Instructor;
  category: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  duration: number; // in minutes, calculated from all lessons
  credits: number;
  rating?: number;
  enrollmentCount: number;
  createdAt: string;
  updatedAt: string;
  price: string; // Decimal field from Django
  is_paid: boolean;
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
  title: string;
  lesson_type: "video" | "blog"; // Only two types in backend
  type: "video" | "blog"; // Alias for lesson_type
  duration?: number; // in minutes
  order: number;
  isCompleted: boolean;
  isLocked: boolean;
  contentUrl?: string;
  created_at: string;
}

export interface Module {
  id: string;
  title: string;
  description: string;
  order: number;
  lessons: Lesson[];
  isCompleted: boolean;
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
  prerequisites: string[];
  learningObjectives: string[];
  instructor: Instructor; // Already has bio and credentials
  modules: Module[];
  averageRating?: number;
  totalReviews: number;
  isEnrolled: boolean;
  progress: number; // 0-100, enrollment progress percentage
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
  lastPosition: number; // video position in seconds
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

export type ApplicationStatus =
  | "pending"
  | "under_review"
  | "approved"
  | "rejected"
  | "cancelled";

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

export interface ForumAuthor {
  id: string;
  fullName: string;
  avatarUrl?: string;
  role: "student" | "teacher" | "admin";
}

export interface ForumPost {
  id: string;
  title: string;
  content: string;
  excerpt: string;
  authorId: string;
  author: ForumAuthor;
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
  author: ForumAuthor;
  parentId?: string;
  replies: ForumComment[];
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
