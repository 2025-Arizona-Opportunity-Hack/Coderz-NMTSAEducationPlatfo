import React from "react";
import { cn } from "@/lib/utils";

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex max-w-[80%]">
      <div
        className={cn(
          "rounded-lg px-4 py-2",
          "bg-palette-gray-light/20 border border-palette-gray-light/30",
        )}
      >
        <span className="flex gap-1">
          <span className={cn("animate-bounce", "text-palette-teal")}>•</span>
          <span
            className={cn("animate-bounce", "text-palette-teal")}
            style={{ animationDelay: "0.2s" }}
          >
            •
          </span>
          <span
            className={cn("animate-bounce", "text-palette-teal")}
            style={{ animationDelay: "0.4s" }}
          >
            •
          </span>
        </span>
      </div>
    </div>
  );
};

export default TypingIndicator;
