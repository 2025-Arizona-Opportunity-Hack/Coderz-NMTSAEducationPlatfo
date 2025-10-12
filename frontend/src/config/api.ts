/**
 * API Configuration and Axios Instance
 * 
 * This module provides a configured Axios instance for making HTTP requests
 * to the Django backend API. It includes:
 * - JWT token authentication
 * - CSRF token support for Django
 * - Request/response interceptors for error handling
 * - Automatic token refresh on 401 errors
 * 
 * @module config/api
 */

import type { ApiError } from "../types/api";

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

/**
 * Base URL for the API
 * Defaults to Django backend running on port 8000
 */
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

/**
 * Configured Axios instance for API requests
 * Uses Auth0 Bearer token authentication
 */
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Auth0 token getter function
 * This will be set by the Auth0Provider wrapper
 */
let getAccessTokenFn: (() => Promise<string>) | null = null;

/**
 * Set the Auth0 token getter function
 * Called by Auth0Provider during initialization
 * 
 * @param {Function} fn - Function that returns Auth0 access token
 */
export function setAuth0TokenGetter(fn: () => Promise<string>): void {
  getAccessTokenFn = fn;
}

/**
 * Request interceptor to add authentication headers
 * - Adds Auth0 Bearer token for authentication
 * - No CSRF needed for Bearer token authentication
 */
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Get Auth0 access token
    if (getAccessTokenFn && config.headers) {
      try {
        const token = await getAccessTokenFn();
        if (token) {
          console.log(`[API] Adding Bearer token to request: ${config.url}`, token.substring(0, 20) + "...");
          config.headers.Authorization = `Bearer ${token}`;
        } else {
          console.warn(`[API] No token available for request: ${config.url}`);
        }
      } catch (error) {
        console.error("[API] Failed to get access token:", error);
      }
    } else {
      console.warn(`[API] Token getter not set for request: ${config.url}`);
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

/**
 * Response interceptor for error handling
 * Handles common HTTP errors and formats them consistently
 * - 401: User will be redirected to Auth0 login by Auth0Provider
 * - 400: Format validation errors from Django
 * - Network errors: Provide user-friendly message
 */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    if (error.response) {
      const { status, data } = error.response;

      // Handle 401 Unauthorized
      // Auth0Provider will handle re-authentication automatically
      if (status === 401) {
        const apiError: ApiError = {
          message: data?.message || "Authentication required",
          statusCode: status,
          errors: data?.errors,
        };
        return Promise.reject(apiError);
      }

      // Handle 400 Bad Request - Django validation errors
      if (status === 400) {
        const apiError: ApiError = {
          message: data?.message || "Validation error",
          statusCode: status,
          errors: data?.errors,
        };
        return Promise.reject(apiError);
      }

      // Handle other error responses
      const apiError: ApiError = {
        message: data?.message || "An error occurred",
        statusCode: status,
        errors: data?.errors,
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
