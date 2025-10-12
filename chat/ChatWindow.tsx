import React, { useState, useRef, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useSelector } from "react-redux";
import type { RootState } from "@/store/store";
import { audioManager } from "@/lib/audio";
import { getSimulatedResponse, Message } from "./utils";
import { clearLocalLLMCache } from "@/lib/webllm"; // only for unload cleanup
import {
  enableGemini,
  getProvider,
  sendChat,
  AIProvider,
  getHistory,
} from "@/lib/ai";
import ChatHeader from "./ChatHeader";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import ChatToggleButton from "./ChatToggleButton";
import TypingIndicator from "./TypingIndicator";
import GenaiDialog from "./GenaiDialog";

const initialMessages: Message[] = [
  {
    id: "1",
    content:
      "Hi! I'm Aakash's portfolio assistant. Ask about skills, projects, education, or experience. Enable AI with a Gemini API key or load a local WebLLM. Local model load can slow this tab and responses, taking several minutes (even ~10) on the first download.",
    sender: "bot",
    timestamp: new Date(),
  },
];

export const ChatWindow: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isTyping, setIsTyping] = useState(false);
  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false);
  const [aiEnabled, setAiEnabled] = useState(false);
  const [provider, setProvider] = useState<AIProvider>("none");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const { soundEnabled } = useSelector((state: RootState) => state.mode);

  // Check if API key is set on component mount
  useEffect(() => {
    // Initialize from gateway state (history may exist if preserved in memory during hot reload)
    const existingProvider = getProvider();
    setProvider(existingProvider);
    setAiEnabled(existingProvider === "gemini" || existingProvider === "local");
    if (getHistory().length > 0) {
      // append any prior history after initial message (avoid duplicating first message)
      const prior = getHistory().map((h, idx) => ({
        id: `rehydrated-${idx}`,
        content: h.content,
        sender: h.role,
        timestamp: new Date(h.ts),
      }));
      if (prior.length) {
        setMessages((prev) => [prev[0], ...prior.slice(1)]); // keep first existing message, replace rest
      }
    }
    const handleUnload = () => {
      clearLocalLLMCache();
    };
    window.addEventListener("beforeunload", handleUnload);
    return () => window.removeEventListener("beforeunload", handleUnload);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when opening chat
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 300);
    }
  }, [isOpen, isMinimized]);

  const toggleChat = () => {
    if (soundEnabled) {
      audioManager.playSoundEffect("click");
    }
    if (!isOpen) {
      setIsOpen(true);
      setIsMinimized(false);
    } else {
      setIsOpen(false);
    }
  };

  const minimizeChat = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (soundEnabled) {
      audioManager.playSoundEffect("click");
    }
    setIsMinimized(!isMinimized);
  };

  const generateUniqueId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  };

  const handleToggleAI = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowApiKeyDialog(true);
  };

  const handleApiKeySubmit = async (apiKey: string) => {
    const resp = await enableGemini(apiKey);
    setAiEnabled(resp.success);
    setProvider(getProvider());
    setShowApiKeyDialog(false);
    const confirmationMessage: Message = {
      id: generateUniqueId(),
      content: resp.content,
      sender: "bot",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, confirmationMessage]);
  };

  const handleLocalStatus = async (statusMessage: string) => {
    // Provider already updated inside toggleLocal; just reflect state
    const current = getProvider();
    setProvider(current);
    setAiEnabled(current === "gemini" || current === "local");
    if (statusMessage) {
      setMessages((prev) => [
        ...prev,
        {
          id: generateUniqueId(),
          content: statusMessage,
          sender: "bot",
          timestamp: new Date(),
        },
      ]);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return; // block multiple concurrent sends

    if (soundEnabled) {
      audioManager.playSoundEffect("message");
    }

    const newUserMessage: Message = {
      id: generateUniqueId(),
      content: inputValue.trim(),
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    const userMessageText = inputValue.trim();
    setInputValue("");
    setIsTyping(true);

    try {
      let botResponse: Message;

      if (aiEnabled && (provider === "gemini" || provider === "local")) {
        const response = await sendChat(userMessageText);
        botResponse = {
          id: generateUniqueId(),
          content: response.success
            ? response.content
            : `⚠️ ${response.content}`,
          sender: "bot",
          timestamp: new Date(),
        };
      } else {
        // Ask for API key for more intelligent responses
        if (Math.random() < 0.3) {
          // 30% chance to prompt for AI
          setShowApiKeyDialog(true);
        }

        // Use simulated response as fallback
        await new Promise((resolve) =>
          setTimeout(resolve, 1000 + Math.random() * 1000),
        );
        botResponse = {
          id: generateUniqueId(),
          content: getSimulatedResponse(userMessageText),
          sender: "bot",
          timestamp: new Date(),
        };
      }

      setMessages((prev) => [...prev, botResponse]);
    } catch {
      const errorMessage: Message = {
        id: generateUniqueId(),
        content: "Sorry, I encountered an error. Please try again.",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <GenaiDialog
        isOpen={showApiKeyDialog}
        onSubmitApiKey={handleApiKeySubmit}
        onUseLocal={handleLocalStatus}
        onClose={() => setShowApiKeyDialog(false)}
      />
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.2 }}
            className={cn(
              "bg-background border rounded-lg shadow-lg overflow-hidden flex flex-col",
              "shadow-[0_4px_20px_rgba(0,0,0,0.15),_0_0_15px_hsl(var(--primary)/0.15)]",
              isMinimized ? "w-72 h-12" : "w-80 sm:w-96 h-96",
            )}
          >
            <ChatHeader
              isTyping={isTyping}
              isMinimized={isMinimized}
              aiEnabled={aiEnabled}
              provider={provider === "regex" ? "none" : provider}
              minimizeChat={minimizeChat}
              closeChat={toggleChat}
              onToggleAI={handleToggleAI}
            />
            {!isMinimized && (
              <>
                <div
                  ref={chatContainerRef}
                  className={cn(
                    "flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin",
                    "bg-card scrollbar-thumb-palette-gray-light/40 scrollbar-track-transparent",
                  )}
                >
                  {messages.map((message) => (
                    <ChatMessage key={message.id} message={message} />
                  ))}
                  {isTyping && <TypingIndicator />}
                  <div ref={messagesEndRef} />
                </div>
                <ChatInput
                  inputValue={inputValue}
                  setInputValue={setInputValue}
                  handleSendMessage={handleSendMessage}
                  inputRef={inputRef as React.RefObject<HTMLTextAreaElement>}
                  isTyping={isTyping}
                />
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
      {!isOpen && <ChatToggleButton toggleChat={toggleChat} />}
    </div>
  );
};

export default ChatWindow;
