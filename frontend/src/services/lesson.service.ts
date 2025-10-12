import type {
  LessonContent,
  Note,
  LessonProgress,
  ApiResponse,
  PaginatedResponse,
} from "../types/api";

import { api } from "../config/api";

export const lessonService = {
  /**
   * Get lesson content with resources and navigation
   */
  async getLessonContent(
    courseId: string,
    lessonId: string,
  ): Promise<LessonContent> {
    const response = await api.get<ApiResponse<LessonContent>>(
      `/student/courses/${courseId}/lessons/${lessonId}`,
    );

    return response.data.data;
  },

  /**
   * Mark lesson as complete
   */
  async markLessonComplete(
    courseId: string,
    lessonId: string,
  ): Promise<LessonProgress> {
    const response = await api.post<ApiResponse<LessonProgress>>(
      `/student/courses/${courseId}/lessons/${lessonId}/complete`,
    );

    return response.data.data;
  },

  /**
   * Update lesson progress (time spent, last position)
   */
  async updateLessonProgress(
    courseId: string,
    lessonId: string,
    progress: Partial<LessonProgress>,
  ): Promise<LessonProgress> {
    const response = await api.put<ApiResponse<LessonProgress>>(
      `/student/courses/${courseId}/lessons/${lessonId}/progress`,
      progress,
    );

    return response.data.data;
  },

  /**
   * Get lesson notes
   */
  async getNotes(
    courseId: string,
    lessonId: string,
  ): Promise<PaginatedResponse<Note>> {
    const response = await api.get<PaginatedResponse<Note>>(
      `/student/courses/${courseId}/lessons/${lessonId}/notes`,
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
      `/student/courses/${courseId}/lessons/${lessonId}/notes`,
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
      `/student/courses/${courseId}/lessons/${lessonId}/notes/${noteId}`,
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
      `/student/courses/${courseId}/lessons/${lessonId}/notes/${noteId}`,
    );
  },
};
