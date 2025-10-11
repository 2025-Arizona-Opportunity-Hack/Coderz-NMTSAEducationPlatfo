import type {
  DashboardStats,
  EnrollmentWithProgress,
  ContinueLearningItem,
  Certificate,
  ApiResponse,
  PaginatedResponse,
} from "../types/api";
import { api } from "../config/api";

export const dashboardService = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    const response = await api.get<ApiResponse<DashboardStats>>(
      "/dashboard/stats",
    );

    return response.data.data;
  },

  /**
   * Get user's enrollments with progress
   */
  async getEnrollments(
    page: number = 1,
    limit: number = 10,
    status?: "in-progress" | "completed",
  ): Promise<PaginatedResponse<EnrollmentWithProgress>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(status && { status }),
    });

    const response = await api.get<PaginatedResponse<EnrollmentWithProgress>>(
      `/dashboard/enrollments?${params}`,
    );

    return response.data;
  },

  /**
   * Get continue learning recommendations
   */
  async getContinueLearning(): Promise<ContinueLearningItem[]> {
    const response = await api.get<ApiResponse<ContinueLearningItem[]>>(
      "/dashboard/continue-learning",
    );

    return response.data.data;
  },

  /**
   * Get user's certificates
   */
  async getCertificates(): Promise<Certificate[]> {
    const response = await api.get<ApiResponse<Certificate[]>>(
      "/dashboard/certificates",
    );

    return response.data.data;
  },

  /**
   * Download certificate
   */
  async downloadCertificate(certificateId: string): Promise<Blob> {
    const response = await api.get(`/certificates/${certificateId}/download`, {
      responseType: "blob",
    });

    return response.data;
  },
};
