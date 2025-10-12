/**
 * Admin Dashboard Types
 * 
 * Type definitions specific to administrator functionality
 * including user management, teacher verification, and system analytics
 * 
 * @module types/admin
 */

import type { Profile, Course } from "./api";

// ============================================================================
// Admin Dashboard Types
// ============================================================================

/**
 * Admin dashboard statistics
 * Provides system-wide overview
 */
export interface AdminStats {
  totalUsers: number;
  totalStudents: number;
  totalInstructors: number;
  totalCourses: number;
  publishedCourses: number;
  pendingApplications: number;
  activeEnrollments: number;
  totalRevenue: number;
  monthlyActiveUsers: number;
  systemHealth: "excellent" | "good" | "warning" | "critical";
}

/**
 * Teacher application for verification
 * Used in admin review process
 */
export interface TeacherApplication {
  id: string;
  teacherId: string;
  teacher: {
    id: string;
    fullName: string;
    email: string;
    avatarUrl?: string;
    bio?: string;
  };
  status: "pending" | "under_review" | "approved" | "rejected";
  submittedAt: string;
  reviewedAt?: string;
  reviewedBy?: string;
  reviewFeedback?: string;
  credentials: {
    id: string;
    name: string;
    fileUrl: string;
    fileType: string;
  }[];
  resume?: {
    fileUrl: string;
    uploadedAt: string;
  };
  experience: string;
  specialization: string[];
  references?: string;
}

/**
 * Course awaiting admin review
 */
export interface CourseReview extends Course {
  teacherId: string;
  teacher: {
    id: string;
    fullName: string;
    email: string;
  };
  submittedForReview: string;
  reviewStatus: "pending" | "approved" | "rejected" | "needs_changes";
  reviewNotes?: string;
  moduleCount: number;
  lessonCount: number;
  isComplete: boolean; // Has all required content
}

/**
 * User management record with admin capabilities
 */
export interface AdminUserRecord extends Profile {
  lastLogin?: string;
  enrollmentCount?: number;
  coursesCreated?: number;
  accountStatus: "active" | "suspended" | "banned";
  verificationStatus?: "verified" | "pending" | "not_verified";
  registeredAt: string;
  totalSpent?: number;
  totalEarned?: number;
}

/**
 * System analytics data
 * Time-series data for various metrics
 */
export interface SystemAnalytics {
  timeframe: "week" | "month" | "year";
  userGrowth: {
    date: string;
    newUsers: number;
    activeUsers: number;
  }[];
  enrollmentGrowth: {
    date: string;
    newEnrollments: number;
    completedCourses: number;
  }[];
  revenueData: {
    date: string;
    revenue: number;
    transactions: number;
  }[];
  topCourses: {
    courseId: string;
    title: string;
    enrollments: number;
    revenue: number;
    rating: number;
  }[];
  topInstructors: {
    instructorId: string;
    name: string;
    coursesCreated: number;
    totalEnrollments: number;
    averageRating: number;
  }[];
  categoryBreakdown: {
    category: string;
    courseCount: number;
    enrollmentCount: number;
  }[];
}

/**
 * Admin action log entry
 * For audit trail purposes
 */
export interface AdminActionLog {
  id: string;
  adminId: string;
  adminName: string;
  action: string;
  targetType: "user" | "course" | "application" | "system";
  targetId: string;
  details: string;
  timestamp: string;
  ipAddress?: string;
}

/**
 * Review action DTO for teacher applications
 */
export interface ReviewTeacherApplicationDto {
  status: "approved" | "rejected";
  feedback?: string;
}

/**
 * Review action DTO for course submissions
 */
export interface ReviewCourseDto {
  status: "approved" | "rejected" | "needs_changes";
  notes?: string;
}

/**
 * User update DTO for admin user management
 */
export interface UpdateUserDto {
  isActive?: boolean;
  accountStatus?: "active" | "suspended" | "banned";
  role?: "student" | "instructor" | "admin";
  email?: string;
  fullName?: string;
}
