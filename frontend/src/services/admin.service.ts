/**
 * Admin Service
 * 
 * API service for administrator functionality including:
 * - System-wide dashboard and analytics
 * - User management
 * - Teacher application review
 * - Course content moderation
 * - System configuration
 * 
 * All endpoints are accessible only to users with 'admin' role
 * Follows Django REST Framework conventions
 * 
 * @module services/admin
 */

import type { Profile, DjangoPaginatedResponse } from "../types/api";
import type {
  AdminStats,
  TeacherApplication,
  CourseReview,
  AdminUserRecord,
  SystemAnalytics,
  ReviewTeacherApplicationDto,
  ReviewCourseDto,
  UpdateUserDto,
} from "../types/admin";
import { api } from "../config/api";

/**
 * Admin Service Class
 * Handles all admin-related API operations
 */
class AdminService {
  // ==========================================================================
  // Dashboard & Analytics
  // ==========================================================================

  /**
   * Get admin dashboard statistics
   * Provides system-wide overview of platform health and activity
   * 
   * @returns {Promise<AdminStats>} Dashboard statistics
   * @throws {ApiError} When request fails
   */
  async getDashboardStats(): Promise<AdminStats> {
    const response = await api.get<AdminStats>("/admin/dashboard/");
    return response.data;
  }

  /**
   * Get detailed system analytics
   * 
   * @param {string} timeframe - Time period for analytics ('week', 'month', 'year')
   * @returns {Promise<SystemAnalytics>} System analytics data
   * @throws {ApiError} When request fails
   */
  async getSystemAnalytics(
    timeframe: "week" | "month" | "year" = "month"
  ): Promise<SystemAnalytics> {
    const response = await api.get<SystemAnalytics>("/admin/analytics/", {
      params: { timeframe },
    });
    return response.data;
  }

  // ==========================================================================
  // User Management
  // ==========================================================================

  /**
   * Get paginated list of users with filtering
   * 
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (1-indexed)
   * @param {string} params.role - Filter by role ('student', 'instructor', 'admin')
   * @param {string} params.search - Search by name or email
   * @param {string} params.status - Filter by account status
   * @returns {Promise<DjangoPaginatedResponse<AdminUserRecord>>} Paginated users
   * @throws {ApiError} When request fails
   */
  async getUsers(params?: {
    page?: number;
    role?: string;
    search?: string;
    status?: string;
  }): Promise<DjangoPaginatedResponse<AdminUserRecord>> {
    const response = await api.get<DjangoPaginatedResponse<AdminUserRecord>>(
      "/admin/users/",
      { params }
    );
    return response.data;
  }

  /**
   * Get single user details by ID
   * 
   * @param {string} userId - User ID
   * @returns {Promise<AdminUserRecord>} User details
   * @throws {ApiError} When user not found or request fails
   */
  async getUserById(userId: string): Promise<AdminUserRecord> {
    const response = await api.get<AdminUserRecord>(`/admin/users/${userId}/`);
    return response.data;
  }

  /**
   * Update user account details
   * 
   * @param {string} userId - User ID to update
   * @param {UpdateUserDto} data - Updated user data
   * @returns {Promise<Profile>} Updated user profile
   * @throws {ApiError} When validation fails or user not found
   * 
   * @example
   * await adminService.updateUser('123', {
   *   isActive: false,
   *   accountStatus: 'suspended'
   * });
   */
  async updateUser(userId: string, data: UpdateUserDto): Promise<Profile> {
    const requestData: Record<string, any> = {};
    
    if (data.isActive !== undefined) requestData.is_active = data.isActive;
    if (data.accountStatus) requestData.account_status = data.accountStatus;
    if (data.role) requestData.role = data.role;
    if (data.email) requestData.email = data.email;
    if (data.fullName) requestData.full_name = data.fullName;

    const response = await api.patch<Profile>(
      `/admin/users/${userId}/`,
      requestData
    );
    return response.data;
  }

  /**
   * Delete a user account
   * 
   * @param {string} userId - User ID to delete
   * @returns {Promise<void>}
   * @throws {ApiError} When deletion fails or user not found
   */
  async deleteUser(userId: string): Promise<void> {
    await api.delete(`/admin/users/${userId}/`);
  }

  /**
   * Suspend user account
   * 
   * @param {string} userId - User ID to suspend
   * @param {string} reason - Reason for suspension
   * @returns {Promise<Profile>} Updated user profile
   * @throws {ApiError} When request fails
   */
  async suspendUser(userId: string, reason?: string): Promise<Profile> {
    const response = await api.post<Profile>(
      `/admin/users/${userId}/suspend/`,
      { reason }
    );
    return response.data;
  }

  /**
   * Reactivate suspended user account
   * 
   * @param {string} userId - User ID to reactivate
   * @returns {Promise<Profile>} Updated user profile
   * @throws {ApiError} When request fails
   */
  async reactivateUser(userId: string): Promise<Profile> {
    const response = await api.post<Profile>(
      `/admin/users/${userId}/reactivate/`
    );
    return response.data;
  }

  // ==========================================================================
  // Teacher Application Management
  // ==========================================================================

  /**
   * Get pending teacher applications for review
   * 
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number
   * @param {string} params.status - Filter by status
   * @returns {Promise<DjangoPaginatedResponse<TeacherApplication>>} Paginated applications
   * @throws {ApiError} When request fails
   */
  async getTeacherApplications(params?: {
    page?: number;
    status?: string;
  }): Promise<DjangoPaginatedResponse<TeacherApplication>> {
    // Map to the correct endpoint from backend
    const response = await api.get<
      DjangoPaginatedResponse<TeacherApplication>
    >("/admin/teachers/pending/", { params });
    return response.data;
  }

  /**
   * Get single teacher application details
   * 
   * @param {string} applicationId - Application ID or teacher ID
   * @returns {Promise<TeacherApplication>} Application details
   * @throws {ApiError} When application not found or request fails
   */
  async getTeacherApplicationById(
    applicationId: string
  ): Promise<TeacherApplication> {
    const response = await api.get<TeacherApplication>(
      `/admin/teachers/${applicationId}/`
    );
    return response.data;
  }

  /**
   * Review and approve/reject teacher application
   * 
   * @param {string} applicationId - Application ID or teacher ID
   * @param {ReviewTeacherApplicationDto} data - Review decision and feedback
   * @returns {Promise<TeacherApplication>} Updated application
   * @throws {ApiError} When validation fails or request fails
   * 
   * @example
   * await adminService.reviewTeacherApplication('123', {
   *   status: 'approved',
   *   feedback: 'Credentials verified. Welcome aboard!'
   * });
   */
  async reviewTeacherApplication(
    applicationId: string,
    data: ReviewTeacherApplicationDto
  ): Promise<TeacherApplication> {
    const response = await api.post<TeacherApplication>(
      `/admin/teachers/${applicationId}/verify/`,
      data
    );
    return response.data;
  }

  // ==========================================================================
  // Course Review & Moderation
  // ==========================================================================

  /**
   * Get courses pending admin review
   * 
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number
   * @param {string} params.status - Filter by review status
   * @returns {Promise<DjangoPaginatedResponse<CourseReview>>} Paginated courses
   * @throws {ApiError} When request fails
   */
  async getCoursesForReview(params?: {
    page?: number;
    status?: string;
  }): Promise<DjangoPaginatedResponse<CourseReview>> {
    const response = await api.get<DjangoPaginatedResponse<CourseReview>>(
      "/admin/courses/review/",
      { params }
    );
    return response.data;
  }

  /**
   * Get single course details for review
   * 
   * @param {string} courseId - Course ID
   * @returns {Promise<CourseReview>} Course review details
   * @throws {ApiError} When course not found or request fails
   */
  async getCourseReviewById(courseId: string): Promise<CourseReview> {
    const response = await api.get<CourseReview>(
      `/admin/courses/${courseId}/`
    );
    return response.data;
  }

  /**
   * Preview course content before review
   * 
   * @param {string} courseId - Course ID
   * @returns {Promise<any>} Course preview data
   * @throws {ApiError} When request fails
   */
  async previewCourse(courseId: string): Promise<any> {
    const response = await api.get(`/admin/courses/${courseId}/preview/`);
    return response.data;
  }

  /**
   * Review and approve/reject/request changes for course
   * 
   * @param {string} courseId - Course ID
   * @param {ReviewCourseDto} data - Review decision and notes
   * @returns {Promise<CourseReview>} Updated course review
   * @throws {ApiError} When validation fails or request fails
   * 
   * @example
   * await adminService.reviewCourse('456', {
   *   status: 'approved',
   *   notes: 'Content meets quality standards. Approved for publication.'
   * });
   */
  async reviewCourse(
    courseId: string,
    data: ReviewCourseDto
  ): Promise<CourseReview> {
    const response = await api.post<CourseReview>(
      `/admin/courses/${courseId}/review/`,
      data
    );
    return response.data;
  }

  /**
   * Unpublish a course (remove from catalog)
   * 
   * @param {string} courseId - Course ID
   * @param {string} reason - Reason for unpublishing
   * @returns {Promise<CourseReview>} Updated course
   * @throws {ApiError} When request fails
   */
  async unpublishCourse(
    courseId: string,
    reason?: string
  ): Promise<CourseReview> {
    const response = await api.post<CourseReview>(
      `/admin/courses/${courseId}/unpublish/`,
      { reason }
    );
    return response.data;
  }

  // ==========================================================================
  // Reports & Data Export
  // ==========================================================================

  /**
   * Export user data to CSV
   * 
   * @param {Object} filters - Export filters
   * @returns {Promise<Blob>} CSV file blob
   * @throws {ApiError} When export fails
   */
  async exportUsers(filters?: {
    role?: string;
    status?: string;
  }): Promise<Blob> {
    const response = await api.get("/admin/users/export/", {
      params: filters,
      responseType: "blob",
    });
    return response.data;
  }

  /**
   * Export analytics data to CSV
   * 
   * @param {string} timeframe - Time period for export
   * @returns {Promise<Blob>} CSV file blob
   * @throws {ApiError} When export fails
   */
  async exportAnalytics(timeframe: string = "month"): Promise<Blob> {
    const response = await api.get("/admin/analytics/export/", {
      params: { timeframe },
      responseType: "blob",
    });
    return response.data;
  }
}

/**
 * Singleton instance of AdminService
 * Use this for all admin-related API operations
 * 
 * @example
 * import { adminService } from '@/services/admin.service';
 * 
 * const stats = await adminService.getDashboardStats();
 */
export const adminService = new AdminService();
