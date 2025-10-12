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
      // Build query params manually to match backend expectations
      const queryParams = new URLSearchParams();

      if (params.page) queryParams.append("page", params.page.toString());
      if (params.limit) queryParams.append("limit", params.limit.toString());
      if (params.search) queryParams.append("search", params.search);
      if (params.category) queryParams.append("category", params.category);
      if (params.difficulty)
        queryParams.append("difficulty", params.difficulty);
      if (params.minCredits)
        queryParams.append("minCredits", params.minCredits.toString());
      if (params.maxCredits)
        queryParams.append("maxCredits", params.maxCredits.toString());
      if (params.minRating)
        queryParams.append("minRating", params.minRating.toString());
      if (params.sortBy) queryParams.append("sortBy", params.sortBy);
      if (params.sortOrder) queryParams.append("sortOrder", params.sortOrder);

      const response = await api.get<PaginatedResponse<Course>>(
        `/courses?${queryParams}`,
      );

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch courses");
    }
  },

  async getCourseById(id: string): Promise<Course> {
    try {
      const response = await api.get<Course>(`/courses/${id}`);

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch course");
    }
  },

  async getCategories(): Promise<string[]> {
    try {
      const response = await api.get<{ data: string[] }>("/courses/categories");

      return response.data.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch categories");
    }
  },

  async getFeaturedCourses(limit: number = 6): Promise<Course[]> {
    try {
      const response = await api.get<{ data: Course[] }>("/courses/featured", {
        params: { limit },
      });

      return response.data.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch featured courses");
    }
  },

  async getCourseDetail(id: string): Promise<CourseDetail> {
    try {
      const response = await api.get<CourseDetail>(`/courses/${id}/detail`);

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to fetch course details");
    }
  },

  async enrollInCourse(courseId: string): Promise<Enrollment> {
    try {
      const response = await api.post<Enrollment>(
        `/courses/${courseId}/enroll`,
      );

      return response.data;
    } catch (error) {
      const apiError = error as ApiError;

      throw new Error(apiError.message || "Failed to enroll in course");
    }
  },

  async unenrollFromCourse(courseId: string): Promise<void> {
    try {
      await api.delete(`/courses/${courseId}/enroll`);
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
        `/courses/${courseId}/reviews`,
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
