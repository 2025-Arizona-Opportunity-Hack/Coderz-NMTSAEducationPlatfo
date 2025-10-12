import type {
  ForumPost,
  ForumComment,
  CreatePostDto,
  UpdatePostDto,
  PaginatedResponse,
} from "../types/api";

import { api } from "../config/api";

interface ForumApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export const forumService = {
  /**
   * Get all forum posts
   */
  async getPosts(
    page: number = 1,
    limit: number = 12,
    search?: string,
    tags?: string[],
    sortBy: "recent" | "popular" = "recent",
  ): Promise<PaginatedResponse<ForumPost>> {
    const params: Record<string, string> = {
      page: page.toString(),
      limit: limit.toString(),
      sortBy,
    };

    if (search) {
      params.search = search;
    }

    // Add tags as array parameters tags[]=tag1&tags[]=tag2
    const queryParams = new URLSearchParams(params);

    if (tags && tags.length > 0) {
      tags.forEach((tag) => {
        queryParams.append("tags[]", tag);
      });
    }

    const response = await api.get<ForumApiResponse<ForumPost[]>>(
      `/forum/posts?${queryParams}`,
    );

    return {
      data: response.data.data,
      pagination: response.data.pagination || {
        page: 1,
        limit: 12,
        total: 0,
        totalPages: 0,
      },
    };
  },

  /**
   * Get a specific forum post by ID
   */
  async getPostById(id: string): Promise<ForumPost> {
    const response = await api.get<ForumApiResponse<ForumPost>>(
      `/forum/posts/${id}`,
    );

    return response.data.data;
  },

  /**
   * Create a new forum post
   */
  async createPost(data: CreatePostDto): Promise<ForumPost> {
    const response = await api.post<ForumApiResponse<ForumPost>>(
      "/forum/posts",
      data,
    );

    return response.data.data;
  },

  /**
   * Update a forum post
   */
  async updatePost(id: string, data: UpdatePostDto): Promise<ForumPost> {
    const response = await api.put<ForumApiResponse<ForumPost>>(
      `/forum/posts/${id}`,
      data,
    );

    return response.data.data;
  },

  /**
   * Delete a forum post
   */
  async deletePost(id: string): Promise<void> {
    await api.delete(`/forum/posts/${id}`);
  },

  /**
   * Like a forum post
   */
  async likePost(id: string): Promise<void> {
    await api.post(`/forum/posts/${id}/like`);
  },

  /**
   * Unlike a forum post
   */
  async unlikePost(id: string): Promise<void> {
    await api.delete(`/forum/posts/${id}/like`);
  },

  /**
   * Get comments for a post
   */
  async getComments(postId: string): Promise<ForumComment[]> {
    const response = await api.get<ForumApiResponse<ForumComment[]>>(
      `/forum/posts/${postId}/comments`,
    );

    return response.data.data;
  },

  /**
   * Create a comment on a post
   */
  async createComment(
    postId: string,
    content: string,
    parentId?: string,
  ): Promise<ForumComment> {
    const response = await api.post<ForumApiResponse<ForumComment>>(
      `/forum/posts/${postId}/comments`,
      { content, parentId },
    );

    return response.data.data;
  },

  /**
   * Like a comment
   */
  async likeComment(id: string): Promise<void> {
    await api.post(`/forum/comments/${id}/like`);
  },

  /**
   * Unlike a comment
   */
  async unlikeComment(id: string): Promise<void> {
    await api.delete(`/forum/comments/${id}/like`);
  },

  /**
   * Get available tags
   */
  async getTags(): Promise<string[]> {
    const response = await api.get<ForumApiResponse<string[]>>("/forum/tags");

    return response.data.data;
  },
};
