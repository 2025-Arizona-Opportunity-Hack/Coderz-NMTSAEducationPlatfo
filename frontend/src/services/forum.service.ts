import type {
  ForumPost,
  ForumComment,
  CreatePostDto,
  UpdatePostDto,
  CreateCommentDto,
  ApiResponse,
  PaginatedResponse,
} from "../types/api";

import { api } from "../config/api";

export const forumService = {
  /**
   * Get all forum posts
   */
  async getPosts(
    page: number = 1,
    limit: number = 10,
    search?: string,
    tags?: string[],
    sortBy: "recent" | "popular" = "recent",
  ): Promise<PaginatedResponse<ForumPost>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      sortBy,
      ...(search && { search }),
      ...(tags && tags.length > 0 && { tags: tags.join(",") }),
    });

    const response = await api.get<PaginatedResponse<ForumPost>>(
      `/forum/posts?${params}`,
    );

    return response.data;
  },

  /**
   * Get a specific forum post by ID
   */
  async getPostById(id: string): Promise<ForumPost> {
    const response = await api.get<ApiResponse<ForumPost>>(
      `/forum/posts/${id}`,
    );

    return response.data.data;
  },

  /**
   * Create a new forum post
   */
  async createPost(data: CreatePostDto): Promise<ForumPost> {
    const response = await api.post<ApiResponse<ForumPost>>(
      "/forum/posts",
      data,
    );

    return response.data.data;
  },

  /**
   * Update a forum post
   */
  async updatePost(id: string, data: UpdatePostDto): Promise<ForumPost> {
    const response = await api.patch<ApiResponse<ForumPost>>(
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
   * Toggle like on a forum post
   */
  async toggleLikePost(id: string): Promise<{ liked: boolean; likes: number }> {
    const response = await api.post<
      ApiResponse<{ liked: boolean; likes: number }>
    >(`/forum/posts/${id}/like`);

    return response.data.data;
  },

  /**
   * Get comments for a post
   */
  async getComments(postId: string): Promise<ForumComment[]> {
    const response = await api.get<ApiResponse<ForumComment[]>>(
      `/forum/posts/${postId}/comments`,
    );

    return response.data.data;
  },

  /**
   * Create a comment on a post
   */
  async createComment(data: CreateCommentDto): Promise<ForumComment> {
    const response = await api.post<ApiResponse<ForumComment>>(
      `/forum/comments`,
      data,
    );

    return response.data.data;
  },

  /**
   * Update a comment
   */
  async updateComment(id: string, content: string): Promise<ForumComment> {
    const response = await api.patch<ApiResponse<ForumComment>>(
      `/forum/comments/${id}`,
      { content },
    );

    return response.data.data;
  },

  /**
   * Delete a comment
   */
  async deleteComment(id: string): Promise<void> {
    await api.delete(`/forum/comments/${id}`);
  },

  /**
   * Toggle like on a comment
   */
  async toggleLikeComment(
    id: string,
  ): Promise<{ liked: boolean; likes: number }> {
    const response = await api.post<
      ApiResponse<{ liked: boolean; likes: number }>
    >(`/forum/comments/${id}/like`);

    return response.data.data;
  },

  /**
   * Get available tags
   */
  async getTags(): Promise<string[]> {
    const response = await api.get<ApiResponse<string[]>>("/forum/tags");

    return response.data.data;
  },
};
