import { useState } from "react";
import "./ReflectionInput.css";

interface ReflectionInputProps {
  onSubmit: (text: string) => void;
  disabled?: boolean;
}

export default function ReflectionInput({ onSubmit, disabled }: ReflectionInputProps) {
  const [text, setText] = useState("");

  const canSend = text.trim().length > 0 && !disabled;

  const handleSubmit = () => {
    if (!canSend) return;
    onSubmit(text.trim());
    setText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="reflection-input">
      <textarea
        className="reflection-input__field"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Share your thoughts..."
        rows={3}
        maxLength={5000}
        disabled={disabled}
        aria-label="Write your reflection"
      />
      <button
        className="reflection-input__send"
        onClick={handleSubmit}
        disabled={!canSend}
        aria-label="Send reflection"
        type="button"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </div>
  );
}
