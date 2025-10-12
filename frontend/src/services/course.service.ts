import type {
  ApiError,
  Course,
  CourseDetail,
  Enrollment,
  PaginatedResponse,
  Review,
} from "../types/api";

import api from "../config/api";

export interface GetCoursesParams {
  page?: number;
  limit?: number;
  search?: string;
  category?: string;
  difficulty?: "beginner" | "intermediate" | "advanced";
  minCredits?: number;
  maxCredits?: number;
  minDuration?: number;
  maxDuration?: number;
  minRating?: number;
  sortBy?: "popularity" | "newest" | "rating" | "title";
  sortOrder?: "asc" | "desc";
}

export const courseService = {
  async getCourses(
    params: GetCoursesParams = {},
  ): Promise<PaginatedResponse<Course>> {
    try {
      const response = await api.get<PaginatedResponse<Course>>(
        "/student/catalog",
        {
          params,
        },
      );

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch courses");
    }
  },

  /**
   * AI-powered contextual course search
   * Uses natural language to find relevant courses
   */
  async searchCoursesContextual(
    query: string,
  ): Promise<{
    query: string;
    count: number;
    courses: Course[];
    ai_enhanced: boolean;
  }> {
    try {
      const response = await api.post<{
        query: string;
        count: number;
        courses: any[];
        ai_enhanced: boolean;
      }>("/search/courses/contextual/", {
        query,
      });

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(
        apiError.message || "Failed to search courses contextually",
      );
    }
  },

  /**
   * Get AI-powered course recommendations based on interests
   */
  async getCourseRecommendations(
    interests?: string,
    limit: number = 5,
  ): Promise<{
    interests: string;
    count: number;
    courses: Course[];
  }> {
    try {
      const params: Record<string, string> = { limit: limit.toString() };

      if (interests) {
        params.interests = interests;
      }

      const response = await api.get<{
        interests: string;
        count: number;
        courses: any[];
      }>("/search/courses/recommendations/", {
        params,
      });

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to get recommendations");
    }
  },

  async getCourseById(id: string): Promise<Course> {
    try {
      const response = await api.get<Course>(`/student/courses/${id}`);

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch course");
    }
  },

  async getCategories(): Promise<string[]> {
    try {
      const response = await api.get<{ data: string[] }>(
        "/student/courses/categories",
      );

      return response.data.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch categories");
    }
  },

  async getFeaturedCourses(limit: number = 6): Promise<Course[]> {
    try {
      const response = await api.get<{ data: Course[] }>(
        "/student/courses/featured",
        {
          params: { limit },
        },
      );

      return response.data.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch featured courses");
    }
  },

  async getCourseDetail(id: string): Promise<CourseDetail> {
    try {
      const response = await api.get<CourseDetail>(
        `/student/courses/${id}/detail`,
      );

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch course details");
    }
  },

  async enrollInCourse(courseId: string): Promise<Enrollment> {
    try {
      const response = await api.post<Enrollment>(
        `/student/courses/${courseId}/enroll`,
      );

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to enroll in course");
    }
  },

  async unenrollFromCourse(courseId: string): Promise<void> {
    try {
      await api.delete(`/student/courses/${courseId}/enroll`);
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to unenroll from course");
    }
  },

  async getCourseReviews(
    courseId: string,
    page: number = 1,
    limit: number = 10,
  ): Promise<PaginatedResponse<Review>> {
    try {
      const response = await api.get<PaginatedResponse<Review>>(
        `/student/courses/${courseId}/reviews`,
        {
          params: { page, limit },
        },
      );

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch course reviews");
    }
  },
};
