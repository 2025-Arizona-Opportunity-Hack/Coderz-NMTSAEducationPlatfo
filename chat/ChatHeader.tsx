import React from "react";
import { MessageSquare, X, Minimize2, ChevronDown, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatHeaderProps {
  isTyping: boolean;
  isMinimized: boolean;
  aiEnabled: boolean;
  // display which provider powers AI
  provider?: "gemini" | "local" | "none";
  minimizeChat: (e: React.MouseEvent) => void;
  closeChat: (e: React.MouseEvent) => void;
  onToggleAI: (e: React.MouseEvent) => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  isTyping,
  isMinimized,
  aiEnabled,
  provider = "none",
  minimizeChat,
  closeChat,
  onToggleAI,
}) => {
  return (
    <div
      className={cn(
        "p-3 flex items-center justify-between cursor-pointer",
        "bg-primary text-primary-foreground",
      )}
      onClick={minimizeChat}
    >
      <div className="flex items-center gap-2">
        <MessageSquare className={cn("h-5 w-5", isTyping && "animate-pulse")} />
        <h3 className="font-medium text-sm">
          {isTyping ? "Bot is typing..." : "Portfolio Assistant"}
        </h3>
        {aiEnabled && (provider === "gemini" || provider === "local") && (
          <div className="text-xs bg-palette-teal-DEFAULT dark:bg-palette-teal-dark text-white px-1.5 py-0.5 rounded-full">
            {provider === "gemini" ? "Gemini" : "Local"}
          </div>
        )}
      </div>
      <div className="flex items-center gap-1">
        {!isMinimized && (
          <>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 rounded-full hover:bg-background/20"
              onClick={(e) => {
                e.stopPropagation();
                onToggleAI(e);
              }}
              aria-label={aiEnabled ? "AI enabled" : "Enable AI"}
              title={
                aiEnabled
                  ? provider === "gemini"
                    ? "AI powered by Gemini"
                    : "AI powered by Local LLM"
                  : "Click to enable AI"
              }
            >
              <Brain className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 rounded-full hover:bg-background/20"
              onClick={(e) => {
                e.stopPropagation();
                minimizeChat(e);
              }}
              aria-label="Minimize chat"
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
          </>
        )}
        {isMinimized && (
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 rounded-full hover:bg-background/20"
            aria-label="Expand chat"
          >
            <ChevronDown className="h-4 w-4" />
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 rounded-full hover:bg-background/20"
          onClick={(e) => {
            e.stopPropagation();
            closeChat(e);
          }}
          aria-label="Close chat"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default ChatHeader;
