import type {
  ChatMessage,
  ChatConversation,
  TypingStatus,
  SendMessageDto,
  MarkAsReadDto,
  ApiResponse,
  PaginatedResponse,
} from "../types/api";

import { api } from "../config/api";

export const chatService = {
  /**
   * Get all conversations for the current user
   */
  async getConversations(
    page: number = 1,
    limit: number = 20,
  ): Promise<PaginatedResponse<ChatConversation>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    const response = await api.get<PaginatedResponse<ChatConversation>>(
      `/chat/conversations?${params}`,
    );

    return response.data;
  },

  /**
   * Get messages for a specific conversation
   */
  async getMessages(
    conversationId: string,
    page: number = 1,
    limit: number = 50,
  ): Promise<PaginatedResponse<ChatMessage>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    const response = await api.get<PaginatedResponse<ChatMessage>>(
      `/chat/conversations/${conversationId}/messages?${params}`,
    );

    return response.data;
  },

  /**
   * Send a new message and get AI response
   */
  async sendMessage(data: SendMessageDto): Promise<{
    userMessage: ChatMessage;
    assistantMessage: ChatMessage;
  }> {
    const response = await api.post<{
      userMessage: ChatMessage;
      assistantMessage: ChatMessage;
    }>("/chat/messages", data);

    return response.data;
  },

  /**
   * Mark messages as read
   */
  async markAsRead(data: MarkAsReadDto): Promise<void> {
    await api.post("/chat/messages/read", data);
  },

  /**
   * Get typing status for a conversation
   */
  async getTypingStatus(conversationId: string): Promise<TypingStatus[]> {
    const response = await api.get<ApiResponse<TypingStatus[]>>(
      `/chat/conversations/${conversationId}/typing`,
    );

    return response.data.data;
  },

  /**
   * Update typing status
   */
  async updateTypingStatus(
    conversationId: string,
    isTyping: boolean,
  ): Promise<void> {
    await api.post(`/chat/conversations/${conversationId}/typing`, {
      isTyping,
    });
  },

  /**
   * Get or create a conversation with a specific user
   */
  async getOrCreateConversation(userId: string): Promise<ChatConversation> {
    const response = await api.post<ApiResponse<ChatConversation>>(
      "/chat/conversations",
      {
        participantId: userId,
      },
    );

    return response.data.data;
  },

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<void> {
    await api.delete(`/chat/conversations/${conversationId}`);
  },

  /**
   * Get unread message count
   */
  async getUnreadCount(): Promise<number> {
    const response =
      await api.get<ApiResponse<{ count: number }>>("/chat/unread-count");

    return response.data.data.count;
  },
};
