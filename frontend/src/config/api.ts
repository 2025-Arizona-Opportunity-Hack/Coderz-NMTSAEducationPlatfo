import type { ApiError } from "../types/api";

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:3000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("auth-token");

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response) {
      // Handle 401 Unauthorized - clear auth and redirect
      if (error.response.status === 401) {
        localStorage.removeItem("auth-token");
        localStorage.removeItem("auth-storage");
        window.location.href = "/login";
      }

      // Return formatted error
      const apiError: ApiError = {
        message: error.response.data?.message || "An error occurred",
        statusCode: error.response.status,
        errors: error.response.data?.errors,
      };

      return Promise.reject(apiError);
    }

    // Network error
    return Promise.reject({
      message: "Network error. Please check your connection.",
      statusCode: 0,
    } as ApiError);
  },
);

export default api;
