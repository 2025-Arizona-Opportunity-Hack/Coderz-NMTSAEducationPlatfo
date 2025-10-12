/**
 * Teacher Dashboard Types
 * 
 * Type definitions specific to teacher/instructor functionality
 * including course management, student progress tracking, and analytics
 * 
 * @module types/teacher
 */

import type { Course } from "./api";

// ============================================================================
// Teacher Dashboard Types
// ============================================================================

/**
 * Teacher dashboard statistics
 * Provides overview of teaching activity
 */
export interface TeacherStats {
  totalCourses: number;
  totalStudents: number;
  totalRevenue: number;
  averageRating: number;
  publishedCourses?: number;
  draftCourses?: number;
  pendingReviewCourses?: number;
}

/**
 * Course creation/update data transfer object
 */
export interface CreateCourseDto {
  title: string;
  description: string;
  category: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  durationMinutes: number;
  credits: number;
  prerequisites?: string;
  learningObjectives?: string[];
  thumbnailUrl?: string;
}

/**
 * Course with additional teacher-specific data
 */
export interface TeacherCourse extends Course {
  status: "draft" | "published" | "pending_review" | "rejected";
  enrolledStudentsCount: number;
  completionRate: number; // percentage
  revenueGenerated?: number;
  lastModified: string;
}

/**
 * Module creation/update DTO
 */
export interface CreateModuleDto {
  title: string;
  description: string;
  order: number;
}

/**
 * Lesson creation/update DTO
 */
export interface CreateLessonDto {
  title: string;
  description: string;
  contentType: "video" | "text" | "quiz" | "assignment";
  content: string;
  order: number;
  durationMinutes?: number;
  videoUrl?: string;
}

/**
 * Student progress in a specific course
 * Used for tracking individual student performance
 */
export interface StudentProgress {
  studentId: string;
  studentName: string;
  studentEmail: string;
  studentAvatar?: string;
  enrolledAt: string;
  lastAccessedAt?: string;
  progressPercentage: number;
  completedLessons: number;
  totalLessons: number;
  timeSpent: number; // in minutes
  certificateEarned: boolean;
  averageQuizScore?: number;
}

/**
 * Course analytics data
 */
export interface CourseAnalytics {
  courseId: string;
  courseTitle: string;
  totalEnrollments: number;
  activeStudents: number;
  completionRate: number; // percentage
  averageCompletionTime: number; // in days
  averageRating: number;
  totalRevenue: number;
  enrollmentTrend: {
    date: string;
    count: number;
  }[];
  lessonEngagement: {
    lessonId: string;
    lessonTitle: string;
    completionRate: number;
    averageTimeSpent: number;
    dropoffRate: number;
  }[];
}

/**
 * Teacher verification status
 */
export interface TeacherVerificationStatus {
  isVerified: boolean;
  verificationDate?: string;
  status: "pending" | "verified" | "rejected" | "not_submitted";
  canCreateCourses: boolean;
  canPublishCourses: boolean;
  rejectionReason?: string;
}
