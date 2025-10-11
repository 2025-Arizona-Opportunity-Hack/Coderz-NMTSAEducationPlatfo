import type {
  Application,
  CreateApplicationDto,
  ApplicationStatus,
  ApiResponse,
  PaginatedResponse,
} from "../types/api";
import { api } from "../config/api";

export const applicationsService = {
  /**
   * Get all applications for the current user
   */
  async getApplications(
    page: number = 1,
    limit: number = 10,
    status?: ApplicationStatus,
  ): Promise<PaginatedResponse<Application>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(status && { status }),
    });

    const response = await api.get<PaginatedResponse<Application>>(
      `/applications?${params}`,
    );

    return response.data;
  },

  /**
   * Get a specific application by ID
   */
  async getApplicationById(id: string): Promise<Application> {
    const response = await api.get<ApiResponse<Application>>(
      `/applications/${id}`,
    );

    return response.data.data;
  },

  /**
   * Create a new certification application
   */
  async createApplication(
    data: CreateApplicationDto,
  ): Promise<Application> {
    const formData = new FormData();

    formData.append("courseId", data.courseId);
    formData.append("motivationStatement", data.motivationStatement);
    formData.append(
      "prerequisitesConfirmed",
      data.prerequisitesConfirmed.toString(),
    );

    if (data.documents) {
      data.documents.forEach((file, index) => {
        formData.append(`documents[${index}]`, file);
      });
    }

    const response = await api.post<ApiResponse<Application>>(
      "/applications",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );

    return response.data.data;
  },

  /**
   * Cancel an application
   */
  async cancelApplication(id: string): Promise<void> {
    await api.patch(`/applications/${id}/cancel`);
  },

  /**
   * Get courses available for application
   */
  async getEligibleCourses(): Promise<
    Array<{
      id: string;
      title: string;
      description: string;
      thumbnailUrl?: string;
      prerequisites: string[];
      instructor: {
        id: string;
        fullName: string;
        avatarUrl?: string;
      };
    }>
  > {
    const response = await api.get<
      ApiResponse<
        Array<{
          id: string;
          title: string;
          description: string;
          thumbnailUrl?: string;
          prerequisites: string[];
          instructor: {
            id: string;
            fullName: string;
            avatarUrl?: string;
          };
        }>
      >
    >("/applications/eligible-courses");

    return response.data.data;
  },
};
