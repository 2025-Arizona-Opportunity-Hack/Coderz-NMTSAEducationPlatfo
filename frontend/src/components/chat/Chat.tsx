/**
 * Modular Chat Interface Component
 *
 * A complete chat system with all functionality driven by backend APIs.
 * No GenAI features included.
 *
 * Features:
 * - Real-time messaging via API
 * - Typing indicators
 * - Message history
 * - Conversation management
 * - Toggle visibility
 * - Error handling
 * - Performance optimized
 */

import type {
  ChatMessage,
  ChatConversation,
  TypingStatus,
} from "../../types/api";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Avatar } from "@heroui/avatar";
import { Spinner } from "@heroui/spinner";
import { Tooltip } from "@heroui/tooltip";
import {
  MessageCircle,
  X,
  Send,
  Minimize2,
  Maximize2,
  Trash2,
} from "lucide-react";

import { chatService } from "../../services/chat.service";

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format timestamp to human-readable format
 */
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return "Just now";
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);

    return `${minutes}m ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);

    return `${hours}h ago`;
  } else if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400);

    return `${days}d ago`;
  } else {
    return date.toLocaleDateString();
  }
};

/**
 * Validate message content
 */
const validateMessage = (
  content: string,
): { valid: boolean; error?: string } => {
  const trimmed = content.trim();

  if (!trimmed) {
    return { valid: false, error: "Message cannot be empty" };
  }

  if (trimmed.length > 1000) {
    return { valid: false, error: "Message is too long (max 1000 characters)" };
  }

  return { valid: true };
};

/**
 * Sanitize message content (basic XSS prevention)
 */
const sanitizeMessage = (content: string): string => {
  return content
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};

/**
 * Format message content with line breaks
 */
const formatMessageContent = (content: string): string => {
  return content.replace(/\n/g, "<br />");
};

/**
 * Debounce function for typing indicator
 */
const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number,
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// ============================================================================
// TYPING INDICATOR COMPONENT
// ============================================================================

interface TypingIndicatorProps {
  typingUsers: TypingStatus[];
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ typingUsers }) => {
  const activeTyping = typingUsers.filter((t) => t.isTyping);

  if (activeTyping.length === 0) return null;

  return (
    <div className="px-4 py-2 text-sm text-default-500">
      <div className="flex items-center gap-2">
        <div className="flex gap-1">
          <span className="w-2 h-2 bg-default-400 rounded-full animate-bounce" />
          <span className="w-2 h-2 bg-default-400 rounded-full animate-bounce [animation-delay:0.2s]" />
          <span className="w-2 h-2 bg-default-400 rounded-full animate-bounce [animation-delay:0.4s]" />
        </div>
        <span>Someone is typing...</span>
      </div>
    </div>
  );
};

// ============================================================================
// CHAT MESSAGE COMPONENT
// ============================================================================

interface ChatMessageProps {
  message: ChatMessage;
  isOwn: boolean;
}

const ChatMessageComponent: React.FC<ChatMessageProps> = ({
  message,
  isOwn,
}) => {
  return (
    <motion.div
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-2 mb-3 ${isOwn ? "flex-row-reverse" : "flex-row"}`}
      initial={{ opacity: 0, y: 10 }}
    >
      <Avatar
        className="flex-shrink-0"
        name={message.sender.fullName}
        size="sm"
        src={message.sender.avatarUrl}
      />
      <div
        className={`flex flex-col ${isOwn ? "items-end" : "items-start"} max-w-[70%]`}
      >
        <div
          className={`px-3 py-2 rounded-lg ${
            isOwn
              ? "bg-primary text-primary-foreground"
              : "bg-default-100 text-foreground"
          }`}
        >
          <p
            dangerouslySetInnerHTML={{
              __html: formatMessageContent(sanitizeMessage(message.content)),
            }}
            className="text-sm break-words"
          />
        </div>
        <span className="text-xs text-default-400 mt-1">
          {formatTimestamp(message.timestamp)}
        </span>
      </div>
    </motion.div>
  );
};

// ============================================================================
// CHAT INPUT COMPONENT
// ============================================================================

interface ChatInputProps {
  onSend: (content: string) => void;
  onTyping: (isTyping: boolean) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onTyping,
  disabled,
}) => {
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleTyping = useCallback(
    debounce((typing: boolean) => {
      onTyping(typing);
    }, 500),
    [onTyping],
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;

    setValue(newValue);
    setError(null);

    if (newValue.trim()) {
      handleTyping(true);
    } else {
      handleTyping(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const validation = validateMessage(value);

    if (!validation.valid) {
      setError(validation.error || "Invalid message");

      return;
    }

    onSend(value.trim());
    setValue("");
    setError(null);
    handleTyping(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <form className="p-4 border-t border-divider" onSubmit={handleSubmit}>
      <div className="flex gap-2">
        <Input
          classNames={{
            input: "text-sm",
            inputWrapper: "h-10",
          }}
          disabled={disabled}
          errorMessage={error}
          isInvalid={!!error}
          placeholder="Type a message..."
          value={value}
          onChange={handleChange}
          onKeyPress={handleKeyPress}
        />
        <Button
          isIconOnly
          className="flex-shrink-0"
          color="primary"
          disabled={disabled || !value.trim()}
          type="submit"
        >
          <Send size={18} />
        </Button>
      </div>
    </form>
  );
};

// ============================================================================
// CHAT HEADER COMPONENT
// ============================================================================

interface ChatHeaderProps {
  conversation: ChatConversation | null;
  isMinimized: boolean;
  onMinimize: () => void;
  onClose: () => void;
  onDelete?: () => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({
  conversation,
  isMinimized,
  onMinimize,
  onClose,
  onDelete,
}) => {
  const assistant = conversation?.participants.find(
    (p) => p.role === "admin" || p.role === "instructor",
  );

  return (
    <div className="flex items-center justify-between p-4 border-b border-divider bg-default-50">
      <div className="flex items-center gap-3">
        {assistant && (
          <>
            <Avatar
              name={assistant.fullName}
              size="sm"
              src={assistant.avatarUrl}
            />
            <div>
              <h3 className="text-sm font-semibold">{assistant.fullName}</h3>
              <p className="text-xs text-default-400">NMTSA Assistant</p>
            </div>
          </>
        )}
        {!assistant && (
          <h3 className="text-sm font-semibold">NMTSA Learn Assistant</h3>
        )}
      </div>
      <div className="flex items-center gap-1">
        {onDelete && conversation && (
          <Tooltip content="Delete conversation">
            <Button isIconOnly size="sm" variant="light" onClick={onDelete}>
              <Trash2 size={16} />
            </Button>
          </Tooltip>
        )}
        <Tooltip content={isMinimized ? "Maximize" : "Minimize"}>
          <Button isIconOnly size="sm" variant="light" onClick={onMinimize}>
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </Button>
        </Tooltip>
        <Tooltip content="Close">
          <Button isIconOnly size="sm" variant="light" onClick={onClose}>
            <X size={16} />
          </Button>
        </Tooltip>
      </div>
    </div>
  );
};

// ============================================================================
// CHAT TOGGLE BUTTON COMPONENT
// ============================================================================

interface ChatToggleButtonProps {
  onClick: () => void;
  unreadCount: number;
}

const ChatToggleButton: React.FC<ChatToggleButtonProps> = ({
  onClick,
  unreadCount,
}) => {
  return (
    <Tooltip content="Open Chat">
      <Button
        isIconOnly
        className="fixed bottom-6 right-6 z-50 shadow-lg"
        color="primary"
        size="lg"
        onClick={onClick}
      >
        <div className="relative">
          <MessageCircle size={24} />
          {unreadCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-danger text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </div>
      </Button>
    </Tooltip>
  );
};

// ============================================================================
// MAIN CHAT WINDOW COMPONENT
// ============================================================================

export const Chat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [activeConversation, setActiveConversation] =
    useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [typingStatuses, setTypingStatuses] = useState<TypingStatus[]>([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Load initial conversation
  const loadConversations = useCallback(async () => {
    try {
      const response = await chatService.getConversations();

      // Set active conversation if not set
      if (!activeConversation && response.data.length > 0) {
        setActiveConversation(response.data[0]);
      }
    } catch (err: any) {
      console.error("Failed to load conversations:", err);
      setError(err.message || "Failed to load conversations");
    }
  }, [activeConversation]);

  // Load messages for active conversation
  const loadMessages = useCallback(async () => {
    if (!activeConversation) return;

    setLoading(true);
    try {
      const response = await chatService.getMessages(activeConversation.id);

      setMessages(response.data);
      scrollToBottom();
    } catch (err: any) {
      console.error("Failed to load messages:", err);
      setError(err.message || "Failed to load messages");
    } finally {
      setLoading(false);
    }
  }, [activeConversation]);

  // Send message
  const handleSendMessage = async (content: string) => {
    if (!activeConversation) return;

    setSending(true);
    setError(null);

    try {
      const response = await chatService.sendMessage({
        content,
        conversationId: activeConversation.id,
      });

      // Add both user message and AI response
      setMessages((prev) => [
        ...prev,
        response.userMessage,
        response.assistantMessage,
      ]);
      scrollToBottom();

      // Update typing status
      await chatService.updateTypingStatus(activeConversation.id, false);
    } catch (err: any) {
      console.error("Failed to send message:", err);
      setError(err.message || "Failed to send message");
    } finally {
      setSending(false);
    }
  };

  // Handle typing status
  const handleTyping = async (isTyping: boolean) => {
    if (!activeConversation) return;

    try {
      await chatService.updateTypingStatus(activeConversation.id, isTyping);
    } catch (err: any) {
      console.error("Failed to update typing status:", err);
    }
  };

  // Poll for new messages and typing status
  const startPolling = useCallback(() => {
    if (pollingIntervalRef.current) return;

    pollingIntervalRef.current = setInterval(async () => {
      if (activeConversation) {
        try {
          // Poll for new messages
          const response = await chatService.getMessages(
            activeConversation.id,
            1,
            10,
          );
          const latestMessages = response.data;

          if (latestMessages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            const newMessages = latestMessages.filter(
              (m) =>
                !lastMessage ||
                new Date(m.timestamp) > new Date(lastMessage.timestamp),
            );

            if (newMessages.length > 0) {
              setMessages((prev) => [...prev, ...newMessages]);
              scrollToBottom();
            }
          }

          // Poll for typing status
          const typingStatus = await chatService.getTypingStatus(
            activeConversation.id,
          );

          setTypingStatuses(typingStatus);
        } catch (err) {
          console.error("Polling error:", err);
        }
      }
    }, 3000); // Poll every 3 seconds
  }, [activeConversation, messages]);

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  // Handle delete conversation
  const handleDeleteConversation = async () => {
    if (!activeConversation) return;

    if (!confirm("Are you sure you want to clear this conversation?")) {
      return;
    }

    setActiveConversation(null);
    setMessages([]);
  };

  // Effects
  useEffect(() => {
    if (isOpen) {
      loadConversations();
    }
  }, [isOpen, loadConversations]);

  useEffect(() => {
    if (activeConversation) {
      loadMessages();
    }
  }, [activeConversation, loadMessages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      startPolling();
    } else {
      stopPolling();
    }

    return () => stopPolling();
  }, [isOpen, isMinimized, startPolling]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <>
      {/* Chat Toggle Button */}
      {!isOpen && (
        <ChatToggleButton unreadCount={0} onClick={() => setIsOpen(true)} />
      )}

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-6 right-6 z-50 w-[380px] bg-background border border-divider rounded-lg shadow-2xl overflow-hidden"
            exit={{ opacity: 0, y: 20 }}
            initial={{ opacity: 0, y: 20 }}
            style={{ maxHeight: isMinimized ? "60px" : "600px" }}
          >
            {/* Header */}
            <ChatHeader
              conversation={activeConversation}
              isMinimized={isMinimized}
              onClose={() => setIsOpen(false)}
              onDelete={
                activeConversation ? handleDeleteConversation : undefined
              }
              onMinimize={() => setIsMinimized(!isMinimized)}
            />

            {/* Content */}
            {!isMinimized && (
              <>
                {/* Error Message */}
                {error && (
                  <div className="px-4 py-2 bg-danger-50 text-danger text-sm">
                    {error}
                  </div>
                )}

                {/* Messages */}
                <div className="h-[440px] overflow-y-auto p-4">
                  {loading ? (
                    <div className="flex items-center justify-center h-full">
                      <Spinner size="lg" />
                    </div>
                  ) : messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-default-400 text-sm text-center px-4">
                      <MessageCircle className="mb-4 opacity-50" size={48} />
                      <p className="font-medium mb-2">
                        Welcome to NMTSA Learn!
                      </p>
                      <p>
                        Ask me anything about our courses, features, or how to
                        get started.
                      </p>
                    </div>
                  ) : (
                    <>
                      {messages.map((message) => (
                        <ChatMessageComponent
                          key={message.id}
                          isOwn={
                            message.sender.role !== "admin" &&
                            message.sender.role !== "instructor"
                          }
                          message={message}
                        />
                      ))}
                      <div ref={messagesEndRef} />
                    </>
                  )}
                </div>

                {/* Typing Indicator */}
                <TypingIndicator typingUsers={typingStatuses} />

                {/* Input */}
                <ChatInput
                  disabled={sending || !activeConversation}
                  onSend={handleSendMessage}
                  onTyping={handleTyping}
                />
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Chat;
