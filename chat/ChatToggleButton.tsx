import React from "react";
import { MessageSquare } from "lucide-react";
import { motion } from "framer-motion";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

interface ChatToggleButtonProps {
  toggleChat: () => void;
}

export const ChatToggleButton: React.FC<ChatToggleButtonProps> = ({
  toggleChat,
}) => {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <motion.button
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={toggleChat}
            className={cn(
              "h-14 w-14 rounded-full flex items-center justify-center shadow-lg transition-colors",
              "bg-palette-teal text-white hover:bg-palette-teal-light",
            )}
            aria-label="Open chat"
          >
            <MessageSquare className="h-6 w-6" />
          </motion.button>
        </TooltipTrigger>
        <TooltipContent side="left">
          Chat with portfolio assistant
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default ChatToggleButton;
