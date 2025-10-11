import type { Course, PaginatedResponse } from "../types/api";
import type { GetCoursesParams } from "../services/course.service";

import { create } from "zustand";

interface CourseFilters {
  search: string;
  category: string;
  difficulty: "" | "beginner" | "intermediate" | "advanced";
  minCredits: number;
  maxCredits: number;
  minDuration: number;
  maxDuration: number;
  minRating: number;
}

interface CourseState {
  courses: Course[];
  filteredCourses: Course[];
  categories: string[];
  filters: CourseFilters;
  sortBy: "popularity" | "newest" | "rating" | "title";
  sortOrder: "asc" | "desc";
  viewMode: "grid" | "list";
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  isLoading: boolean;
  error: string | null;

  // Actions
  setCourses: (data: PaginatedResponse<Course>) => void;
  setCategories: (categories: string[]) => void;
  setFilter: (key: keyof CourseFilters, value: string | number) => void;
  clearFilters: () => void;
  setSortBy: (
    sortBy: "popularity" | "newest" | "rating" | "title",
    sortOrder?: "asc" | "desc",
  ) => void;
  setViewMode: (mode: "grid" | "list") => void;
  setPage: (page: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  getFilterParams: () => GetCoursesParams;
}

const initialFilters: CourseFilters = {
  search: "",
  category: "",
  difficulty: "",
  minCredits: 0,
  maxCredits: 100,
  minDuration: 0,
  maxDuration: 1000,
  minRating: 0,
};

export const useCourseStore = create<CourseState>((set, get) => ({
  courses: [],
  filteredCourses: [],
  categories: [],
  filters: initialFilters,
  sortBy: "popularity",
  sortOrder: "desc",
  viewMode: "grid",
  pagination: {
    page: 1,
    limit: 12,
    total: 0,
    totalPages: 0,
  },
  isLoading: false,
  error: null,

  setCourses: (data) =>
    set({
      courses: data.data,
      filteredCourses: data.data,
      pagination: data.pagination,
      isLoading: false,
      error: null,
    }),

  setCategories: (categories) => set({ categories }),

  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
      pagination: { ...state.pagination, page: 1 }, // Reset to first page
    })),

  clearFilters: () =>
    set({
      filters: initialFilters,
      pagination: { ...get().pagination, page: 1 },
    }),

  setSortBy: (sortBy, sortOrder = "desc") =>
    set({
      sortBy,
      sortOrder,
    }),

  setViewMode: (mode) => set({ viewMode: mode }),

  setPage: (page) =>
    set((state) => ({
      pagination: { ...state.pagination, page },
    })),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error, isLoading: false }),

  getFilterParams: (): GetCoursesParams => {
    const state = get();
    const params: GetCoursesParams = {
      page: state.pagination.page,
      limit: state.pagination.limit,
      sortBy: state.sortBy,
      sortOrder: state.sortOrder,
    };

    if (state.filters.search) params.search = state.filters.search;
    if (state.filters.category) params.category = state.filters.category;
    if (state.filters.difficulty) params.difficulty = state.filters.difficulty;
    if (state.filters.minCredits > 0)
      params.minCredits = state.filters.minCredits;
    if (state.filters.maxCredits < 100)
      params.maxCredits = state.filters.maxCredits;
    if (state.filters.minDuration > 0)
      params.minDuration = state.filters.minDuration;
    if (state.filters.maxDuration < 1000)
      params.maxDuration = state.filters.maxDuration;
    if (state.filters.minRating > 0) params.minRating = state.filters.minRating;

    return params;
  },
}));
