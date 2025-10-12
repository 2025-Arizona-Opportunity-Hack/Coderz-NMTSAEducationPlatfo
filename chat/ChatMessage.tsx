import React from "react";
import { cn } from "@/lib/utils";
import { Message } from "./utils";
import ReactMarkdown from "react-markdown";

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === "user";

  // Custom renderer for links to make them open in new tab and have proper styling
  const customLinkRenderer = (props: any) => {
    const { node, children, href } = props;
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-palette-teal-DEFAULT dark:text-palette-teal-dark underline hover:text-palette-teal-DEFAULT/80 dark:hover:text-palette-teal-dark/80 transition-colors"
      >
        {children}
      </a>
    );
  };

  return (
    <div
      className={cn(
        "flex flex-col max-w-[80%] mb-2",
        isUser ? "ml-auto items-end" : "mr-auto items-start",
      )}
    >
      <div
        className={cn(
          "rounded-lg px-3 py-2",
          isUser
            ? "bg-palette-teal-DEFAULT dark:bg-palette-teal-dark text-white dark:text-foreground"
            : "bg-muted/30 text-foreground border border-border",
        )}
      >
        {isUser ? (
          message.content
        ) : (
          <div className="markdown-content">
            <ReactMarkdown
              components={{
                a: customLinkRenderer,
                p: ({ node, children }) => <p className="mb-2">{children}</p>,
                ul: ({ node, children }) => (
                  <ul className="list-disc pl-4 mb-2">{children}</ul>
                ),
                ol: ({ node, children }) => (
                  <ol className="list-decimal pl-4 mb-2">{children}</ol>
                ),
                li: ({ node, children }) => (
                  <li className="mb-1">{children}</li>
                ),
                strong: ({ node, children }) => (
                  <strong className="font-semibold">{children}</strong>
                ),
                h1: ({ node, children }) => (
                  <h1 className="text-xl font-bold mb-2">{children}</h1>
                ),
                h2: ({ node, children }) => (
                  <h2 className="text-lg font-bold mb-2">{children}</h2>
                ),
                h3: ({ node, children }) => (
                  <h3 className="text-base font-bold mb-1">{children}</h3>
                ),
                pre: ({ node, children }) => (
                  <pre className="bg-palette-gray-light/10 p-2 rounded my-2 overflow-x-auto">
                    {children}
                  </pre>
                ),
                code: ({ node, className, inline, children, ...props }: any) =>
                  inline ? (
                    <code className="bg-palette-gray-light/10 px-1 py-0.5 rounded">
                      {children}
                    </code>
                  ) : (
                    <code className="block">{children}</code>
                  ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
      <span className="text-xs mt-1 opacity-50">
        {message.timestamp.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })}
      </span>
    </div>
  );
};

export default ChatMessage;
