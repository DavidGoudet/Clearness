import type { ReactNode } from "react";
import { useEffect, useRef } from "react";
import type { ChatMessage } from "../../types/api";
import ChatBubble from "./ChatBubble";
import TypingIndicator from "./TypingIndicator";
import "./ChatMessageList.css";

interface ChatMessageListProps {
  messages: ChatMessage[];
  isTyping: boolean;
  children?: ReactNode;
}

export default function ChatMessageList({ messages, isTyping, children }: ChatMessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping, children]);

  return (
    <div className="chat-message-list">
      {messages.map((msg) => (
        <ChatBubble key={msg.id} message={msg} />
      ))}
      {isTyping && <TypingIndicator />}
      {children}
      <div ref={bottomRef} />
    </div>
  );
}
