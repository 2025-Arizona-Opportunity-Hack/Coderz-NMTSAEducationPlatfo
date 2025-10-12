/**
 * Teacher Service
 * 
 * API service for teacher/instructor functionality including:
 * - Course management (CRUD operations)
 * - Module and lesson management
 * - Student progress tracking
 * - Analytics and reporting
 * - Publishing and verification
 * 
 * All endpoints are accessible to users with 'instructor' role
 * Follows Django REST Framework conventions
 * 
 * @module services/teacher
 */

import type {
  DjangoPaginatedResponse,
  Course,
  Module,
  Lesson,
} from "../types/api";
import type {
  TeacherStats,
  CreateCourseDto,
  TeacherCourse,
  CreateModuleDto,
  CreateLessonDto,
  StudentProgress,
  CourseAnalytics,
  TeacherVerificationStatus,
} from "../types/teacher";
import { api } from "../config/api";

/**
 * Teacher Service Class
 * Handles all teacher-related API operations
 */
class TeacherService {
  // ==========================================================================
  // Dashboard & Statistics
  // ==========================================================================

  /**
   * Get teacher dashboard statistics
   * 
   * @returns {Promise<TeacherStats>} Dashboard statistics
   * @throws {ApiError} When request fails
   */
  async getDashboardStats(): Promise<TeacherStats> {
    const response = await api.get<TeacherStats>("/teacher/dashboard/");
    return response.data;
  }

  /**
   * Get teacher verification status
   * 
   * @returns {Promise<TeacherVerificationStatus>} Verification status
   * @throws {ApiError} When request fails
   */
  async getVerificationStatus(): Promise<TeacherVerificationStatus> {
    const response = await api.get<TeacherVerificationStatus>(
      "/teacher/verification/"
    );
    return response.data;
  }

  // ==========================================================================
  // Course Management
  // ==========================================================================

  /**
   * Get list of teacher's courses with pagination
   * 
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (1-indexed)
   * @param {string} params.status - Filter by status (draft, published, etc.)
   * @param {string} params.search - Search query
   * @returns {Promise<DjangoPaginatedResponse<TeacherCourse>>} Paginated courses
   * @throws {ApiError} When request fails
   */
  async getMyCourses(params?: {
    page?: number;
    status?: string;
    search?: string;
  }): Promise<DjangoPaginatedResponse<TeacherCourse>> {
    const response = await api.get<DjangoPaginatedResponse<TeacherCourse>>(
      "/teacher/courses/",
      { params }
    );
    return response.data;
  }

  /**
   * Get single course details by ID
   * 
   * @param {string} courseId - Course ID
   * @returns {Promise<TeacherCourse>} Course details
   * @throws {ApiError} When request fails or course not found
   */
  async getCourseById(courseId: string): Promise<TeacherCourse> {
    const response = await api.get<TeacherCourse>(
      `/teacher/courses/${courseId}/`
    );
    return response.data;
  }

  /**
   * Create a new course
   * 
   * @param {CreateCourseDto} data - Course creation data
   * @returns {Promise<Course>} Created course
   * @throws {ApiError} When validation fails or request fails
   * 
   * @example
   * const course = await teacherService.createCourse({
   *   title: "Introduction to Music Therapy",
   *   description: "Learn the basics...",
   *   category: "music-therapy",
   *   difficulty: "beginner",
   *   durationMinutes: 120,
   *   credits: 3
   * });
   */
  async createCourse(data: CreateCourseDto): Promise<Course> {
    const response = await api.post<Course>("/teacher/courses/create/", {
      title: data.title,
      description: data.description,
      category: data.category,
      difficulty: data.difficulty,
      duration_minutes: data.durationMinutes,
      credits: data.credits,
      prerequisites: data.prerequisites,
      learning_objectives: data.learningObjectives,
      thumbnail_url: data.thumbnailUrl,
    });
    return response.data;
  }

  /**
   * Update existing course
   * 
   * @param {string} courseId - Course ID to update
   * @param {Partial<CreateCourseDto>} data - Updated course data
   * @returns {Promise<Course>} Updated course
   * @throws {ApiError} When validation fails or course not found
   */
  async updateCourse(
    courseId: string,
    data: Partial<CreateCourseDto>
  ): Promise<Course> {
    const requestData: Record<string, any> = {};
    
    if (data.title) requestData.title = data.title;
    if (data.description) requestData.description = data.description;
    if (data.category) requestData.category = data.category;
    if (data.difficulty) requestData.difficulty = data.difficulty;
    if (data.durationMinutes) requestData.duration_minutes = data.durationMinutes;
    if (data.credits) requestData.credits = data.credits;
    if (data.prerequisites) requestData.prerequisites = data.prerequisites;
    if (data.learningObjectives) requestData.learning_objectives = data.learningObjectives;
    if (data.thumbnailUrl) requestData.thumbnail_url = data.thumbnailUrl;

    const response = await api.patch<Course>(
      `/teacher/courses/${courseId}/update/`,
      requestData
    );
    return response.data;
  }

  /**
   * Delete a course
   * 
   * @param {string} courseId - Course ID to delete
   * @returns {Promise<void>}
   * @throws {ApiError} When deletion fails or course not found
   */
  async deleteCourse(courseId: string): Promise<void> {
    await api.delete(`/teacher/courses/${courseId}/delete/`);
  }

  /**
   * Publish a course (make it available to students)
   * 
   * @param {string} courseId - Course ID to publish
   * @returns {Promise<Course>} Published course
   * @throws {ApiError} When course is not ready or request fails
   */
  async publishCourse(courseId: string): Promise<Course> {
    const response = await api.post<Course>(
      `/teacher/courses/${courseId}/publish/`
    );
    return response.data;
  }

  /**
   * Unpublish a course (remove from public catalog)
   * 
   * @param {string} courseId - Course ID to unpublish
   * @returns {Promise<Course>} Unpublished course
   * @throws {ApiError} When request fails
   */
  async unpublishCourse(courseId: string): Promise<Course> {
    const response = await api.post<Course>(
      `/teacher/courses/${courseId}/unpublish/`
    );
    return response.data;
  }

  // ==========================================================================
  // Module Management
  // ==========================================================================

  /**
   * Create a new module in a course
   * 
   * @param {string} courseId - Course ID
   * @param {CreateModuleDto} data - Module creation data
   * @returns {Promise<Module>} Created module
   * @throws {ApiError} When validation fails or request fails
   */
  async createModule(
    courseId: string,
    data: CreateModuleDto
  ): Promise<Module> {
    const response = await api.post<Module>(
      `/teacher/courses/${courseId}/modules/`,
      data
    );
    return response.data;
  }

  /**
   * Update an existing module
   * 
   * @param {string} courseId - Course ID
   * @param {string} moduleId - Module ID to update
   * @param {Partial<CreateModuleDto>} data - Updated module data
   * @returns {Promise<Module>} Updated module
   * @throws {ApiError} When validation fails or module not found
   */
  async updateModule(
    courseId: string,
    moduleId: string,
    data: Partial<CreateModuleDto>
  ): Promise<Module> {
    const response = await api.patch<Module>(
      `/teacher/courses/${courseId}/modules/${moduleId}/update/`,
      data
    );
    return response.data;
  }

  /**
   * Delete a module
   * 
   * @param {string} courseId - Course ID
   * @param {string} moduleId - Module ID to delete
   * @returns {Promise<void>}
   * @throws {ApiError} When deletion fails or module not found
   */
  async deleteModule(courseId: string, moduleId: string): Promise<void> {
    await api.delete(`/teacher/courses/${courseId}/modules/${moduleId}/delete/`);
  }

  // ==========================================================================
  // Lesson Management
  // ==========================================================================

  /**
   * Create a new lesson in a module
   * 
   * @param {string} courseId - Course ID
   * @param {string} moduleId - Module ID
   * @param {CreateLessonDto} data - Lesson creation data
   * @returns {Promise<Lesson>} Created lesson
   * @throws {ApiError} When validation fails or request fails
   */
  async createLesson(
    courseId: string,
    moduleId: string,
    data: CreateLessonDto
  ): Promise<Lesson> {
    const response = await api.post<Lesson>(
      `/teacher/courses/${courseId}/modules/${moduleId}/lessons/`,
      {
        title: data.title,
        description: data.description,
        content_type: data.contentType,
        content: data.content,
        order: data.order,
        duration_minutes: data.durationMinutes,
        video_url: data.videoUrl,
      }
    );
    return response.data;
  }

  /**
   * Update an existing lesson
   * 
   * @param {string} courseId - Course ID
   * @param {string} moduleId - Module ID
   * @param {string} lessonId - Lesson ID to update
   * @param {Partial<CreateLessonDto>} data - Updated lesson data
   * @returns {Promise<Lesson>} Updated lesson
   * @throws {ApiError} When validation fails or lesson not found
   */
  async updateLesson(
    courseId: string,
    moduleId: string,
    lessonId: string,
    data: Partial<CreateLessonDto>
  ): Promise<Lesson> {
    const requestData: Record<string, any> = {};
    
    if (data.title) requestData.title = data.title;
    if (data.description) requestData.description = data.description;
    if (data.contentType) requestData.content_type = data.contentType;
    if (data.content) requestData.content = data.content;
    if (data.order !== undefined) requestData.order = data.order;
    if (data.durationMinutes) requestData.duration_minutes = data.durationMinutes;
    if (data.videoUrl) requestData.video_url = data.videoUrl;

    const response = await api.patch<Lesson>(
      `/teacher/courses/${courseId}/modules/${moduleId}/lessons/${lessonId}/update/`,
      requestData
    );
    return response.data;
  }

  /**
   * Delete a lesson
   * 
   * @param {string} courseId - Course ID
   * @param {string} moduleId - Module ID
   * @param {string} lessonId - Lesson ID to delete
   * @returns {Promise<void>}
   * @throws {ApiError} When deletion fails or lesson not found
   */
  async deleteLesson(
    courseId: string,
    moduleId: string,
    lessonId: string
  ): Promise<void> {
    await api.delete(
      `/teacher/courses/${courseId}/modules/${moduleId}/lessons/${lessonId}/delete/`
    );
  }

  /**
   * Upload video file for a lesson
   * 
   * @param {string} courseId - Course ID
   * @param {string} moduleId - Module ID
   * @param {string} lessonId - Lesson ID
   * @param {File} file - Video file to upload
   * @param {Function} onProgress - Upload progress callback (0-100)
   * @returns {Promise<{ videoUrl: string }>} Uploaded video URL
   * @throws {ApiError} When upload fails or file is invalid
   */
  async uploadLessonVideo(
    courseId: string,
    moduleId: string,
    lessonId: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<{ videoUrl: string }> {
    const formData = new FormData();
    formData.append("video", file);

    const response = await api.post<{ videoUrl: string; video_url: string }>(
      `/teacher/courses/${courseId}/modules/${moduleId}/lessons/${lessonId}/upload/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentage = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(percentage);
          }
        },
      }
    );

    return {
      videoUrl: response.data.videoUrl || response.data.video_url,
    };
  }

  // ==========================================================================
  // Student Progress & Analytics
  // ==========================================================================

  /**
   * Get student progress for a specific course
   * 
   * @param {string} courseId - Course ID
   * @returns {Promise<StudentProgress[]>} List of student progress records
   * @throws {ApiError} When request fails
   */
  async getStudentProgress(courseId: string): Promise<StudentProgress[]> {
    const response = await api.get<DjangoPaginatedResponse<StudentProgress>>(
      `/teacher/courses/${courseId}/analytics/`
    );
    return response.data.results;
  }

  /**
   * Get detailed analytics for a course
   * 
   * @param {string} courseId - Course ID
   * @returns {Promise<CourseAnalytics>} Course analytics data
   * @throws {ApiError} When request fails
   */
  async getCourseAnalytics(courseId: string): Promise<CourseAnalytics> {
    const response = await api.get<CourseAnalytics>(
      `/teacher/courses/${courseId}/analytics/`
    );
    return response.data;
  }

  /**
   * Export course data to CSV
   * 
   * @returns {Promise<Blob>} CSV file blob
   * @throws {ApiError} When export fails
   */
  async exportCourses(): Promise<Blob> {
    const response = await api.get("/teacher/courses/export/", {
      responseType: "blob",
    });
    return response.data;
  }
}

/**
 * Singleton instance of TeacherService
 * Use this for all teacher-related API operations
 * 
 * @example
 * import { teacherService } from '@/services/teacher.service';
 * 
 * const courses = await teacherService.getMyCourses();
 */
export const teacherService = new TeacherService();
