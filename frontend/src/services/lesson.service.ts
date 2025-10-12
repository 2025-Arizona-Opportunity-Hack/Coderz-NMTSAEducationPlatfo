import type {
  LessonContent,
  Note,
  LessonProgress,
  ApiResponse,
  PaginatedResponse,
} from "../types/api";

import { api } from "../config/api";

// Note: These endpoints are placeholders. The backend currently has template-based views
// for lesson functionality that need to be exposed as REST APIs.
// Backend template URLs:
// - /student/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/ - lesson view
// - /student/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/complete/ - mark complete
// - /student/api/save-video-progress/ - save video progress

export const lessonService = {
  /**
   * Get lesson content with resources and navigation
   * TODO: Backend needs to expose this as REST API
   * Current: Template-based view at /student/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/
   */
  async getLessonContent(
    courseId: string,
    lessonId: string,
  ): Promise<LessonContent> {
    const response = await api.get<ApiResponse<LessonContent>>(
      `/courses/${courseId}/lessons/${lessonId}`,
    );

    return response.data.data;
  },

  /**
   * Mark lesson as complete
   * TODO: Backend needs to expose this as REST API
   * Current: Template-based POST to /student/courses/<course_id>/modules/<module_id>/lessons/<lesson_id>/complete/
   */
  async markLessonComplete(
    courseId: string,
    lessonId: string,
  ): Promise<LessonProgress> {
    const response = await api.post<ApiResponse<LessonProgress>>(
      `/courses/${courseId}/lessons/${lessonId}/complete`,
    );

    return response.data.data;
  },

  /**
   * Update lesson progress (time spent, last position)
   * TODO: Backend needs to expose this as REST API
   * Current: Template-based POST to /student/api/save-video-progress/
   */
  async updateLessonProgress(
    courseId: string,
    lessonId: string,
    progress: Partial<LessonProgress>,
  ): Promise<LessonProgress> {
    const response = await api.put<ApiResponse<LessonProgress>>(
      `/courses/${courseId}/lessons/${lessonId}/progress`,
      progress,
    );

    return response.data.data;
  },

  /**
   * Save video progress (backend-specific endpoint)
   * Uses existing backend endpoint: /student/api/save-video-progress/
   */
  async saveVideoProgress(
    enrollmentId: string,
    lessonId: string,
    lastPositionSeconds: number,
    completedPercentage: number,
  ): Promise<void> {
    await api.post("/student/api/save-video-progress/", {
      enrollment_id: enrollmentId,
      lesson_id: lessonId,
      last_position_seconds: lastPositionSeconds,
      completed_percentage: completedPercentage,
    });
  },

  /**
   * Get lesson notes
   */
  async getNotes(
    courseId: string,
    lessonId: string,
  ): Promise<PaginatedResponse<Note>> {
    const response = await api.get<PaginatedResponse<Note>>(
      `/courses/${courseId}/lessons/${lessonId}/notes`,
    );

    return response.data;
  },

  /**
   * Create a new note
   */
  async createNote(
    courseId: string,
    lessonId: string,
    content: string,
    timestamp?: number,
  ): Promise<Note> {
    const response = await api.post<ApiResponse<Note>>(
      `/courses/${courseId}/lessons/${lessonId}/notes`,
      { content, timestamp },
    );

    return response.data.data;
  },

  /**
   * Update an existing note
   */
  async updateNote(
    courseId: string,
    lessonId: string,
    noteId: string,
    content: string,
  ): Promise<Note> {
    const response = await api.put<ApiResponse<Note>>(
      `/courses/${courseId}/lessons/${lessonId}/notes/${noteId}`,
      { content },
    );

    return response.data.data;
  },

  /**
   * Delete a note
   */
  async deleteNote(
    courseId: string,
    lessonId: string,
    noteId: string,
  ): Promise<void> {
    await api.delete(
      `/courses/${courseId}/lessons/${lessonId}/notes/${noteId}`,
    );
  },
};
