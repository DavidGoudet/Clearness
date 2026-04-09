import type { ChatMessage } from "../../types/api";
import "./ChatBubble.css";

interface ChatBubbleProps {
  message: ChatMessage;
}

export default function ChatBubble({ message }: ChatBubbleProps) {
  const isBot = message.sender === "bot";

  return (
    <div className={`chat-bubble chat-bubble--${isBot ? "bot" : "user"}`}>
      {message.content}
    </div>
  );
}
