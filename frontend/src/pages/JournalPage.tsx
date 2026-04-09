import { useCallback, useEffect, useRef, useState } from "react";
import type { ChatMessage, DailyChat } from "../types/api";
import type { MoodOption } from "../constants/moods";
import { getTodayChat, patchChatMood, patchChatReflection } from "../services/chat";
import ChatMessageList from "../components/chat/ChatMessageList";
import MoodSelector from "../components/chat/MoodSelector";
import ReflectionInput from "../components/chat/ReflectionInput";
import "./JournalPage.css";

function getLocalDateString(): string {
  return new Date().toLocaleDateString("en-CA");
}

function chatHasUserMessages(chat: DailyChat): boolean {
  return chat.messages.some((msg) => msg.sender === "user");
}

let nextSyntheticId = -1;

export default function JournalPage() {
  const [chat, setChat] = useState<DailyChat | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [visibleMessages, setVisibleMessages] = useState<ChatMessage[]>([]);
  const [isSavingMood, setIsSavingMood] = useState(false);
  const [isSendingReflection, setIsSendingReflection] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pendingRevealRef = useRef<ChatMessage[] | null>(null);

  const fetchChat = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const localDate = getLocalDateString();
      const data = await getTodayChat(localDate);
      setChat(data);

      // AC3: Existing chat with user messages — show all immediately
      if (chatHasUserMessages(data)) {
        setVisibleMessages(data.messages);
        setIsTyping(false);
      } else {
        // AC2: New chat — show typing indicator, then reveal messages
        setVisibleMessages([]);
        setIsTyping(true);
      }
    } catch {
      setError("Something went wrong loading your journal. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChat();
  }, [fetchChat]);

  // Reveal messages after typing indicator delay
  useEffect(() => {
    if (!isTyping) return;

    const messagesToReveal = pendingRevealRef.current ?? chat?.messages;
    if (!messagesToReveal) return;

    const timer = setTimeout(() => {
      setIsTyping(false);
      setVisibleMessages(messagesToReveal);
      pendingRevealRef.current = null;
    }, 1500);

    return () => clearTimeout(timer);
  }, [isTyping, chat]);

  const showMoodSelector =
    chat !== null &&
    chat.mood === "" &&
    !isTyping &&
    visibleMessages.length > 0;

  const showReflectionInput =
    chat !== null &&
    chat.mood !== "" &&
    chat.status === "in_progress" &&
    !isTyping &&
    visibleMessages.some((m) => m.message_type === "reflection_prompt");

  const handleMoodSelect = useCallback(
    async (option: MoodOption) => {
      if (!chat || isSavingMood) return;

      setIsSavingMood(true);

      // Optimistic: add synthetic user bubble and hide selector
      const syntheticMessage: ChatMessage = {
        id: nextSyntheticId--,
        sender: "user",
        message_type: "mood_response",
        content: `${option.label} ${option.emoji}`,
        order: visibleMessages.length,
        created_at: new Date().toISOString(),
      };

      const previousMessages = visibleMessages;
      setVisibleMessages((prev) => [...prev, syntheticMessage]);
      // Optimistically hide selector by setting mood
      setChat((prev) => (prev ? { ...prev, mood: option.value } : prev));

      try {
        const updated = await patchChatMood(chat.id, option.value);
        setChat(updated);

        // Show mood_response immediately, then type the reflection_prompt
        const moodResponseMessages = updated.messages.filter(
          (m) => m.message_type !== "reflection_prompt"
        );
        setVisibleMessages(moodResponseMessages);

        // Trigger typing indicator to reveal reflection_prompt
        pendingRevealRef.current = updated.messages;
        setIsTyping(true);
      } catch {
        // Rollback on failure
        setVisibleMessages(previousMessages);
        setChat((prev) => (prev ? { ...prev, mood: "" } : prev));
        setError("Failed to save your mood. Please try again.");
      } finally {
        setIsSavingMood(false);
      }
    },
    [chat, isSavingMood, visibleMessages],
  );

  const handleReflectionSubmit = useCallback(
    async (text: string) => {
      if (!chat || isSendingReflection) return;

      setIsSendingReflection(true);

      // Optimistic: show user message immediately
      const syntheticUserMsg: ChatMessage = {
        id: nextSyntheticId--,
        sender: "user",
        message_type: "reflection_response",
        content: text,
        order: visibleMessages.length,
        created_at: new Date().toISOString(),
      };

      const previousMessages = visibleMessages;
      const previousChat = chat;
      setVisibleMessages((prev) => [...prev, syntheticUserMsg]);
      // Hide input by optimistically marking completed
      setChat((prev) => (prev ? { ...prev, status: "completed" as const } : prev));

      try {
        const updated = await patchChatReflection(chat.id, text);
        setChat(updated);

        // Show all messages except the acknowledgment, then type it in
        const withoutAck = updated.messages.filter(
          (m) => m.message_type !== "acknowledgment"
        );
        setVisibleMessages(withoutAck);

        // Trigger typing to reveal the acknowledgment
        pendingRevealRef.current = updated.messages;
        setIsTyping(true);
      } catch {
        // Rollback on failure
        setVisibleMessages(previousMessages);
        setChat(previousChat);
        setError("Failed to save your reflection. Please try again.");
      } finally {
        setIsSendingReflection(false);
      }
    },
    [chat, isSendingReflection, visibleMessages],
  );

  if (isLoading) {
    return (
      <div className="journal-page">
        <h2 className="journal-page__header">Journal</h2>
        <div className="journal-page__loading">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="journal-page">
        <h2 className="journal-page__header">Journal</h2>
        <div className="journal-page__error">{error}</div>
      </div>
    );
  }

  return (
    <div className="journal-page">
      <h2 className="journal-page__header">Journal</h2>
      <ChatMessageList messages={visibleMessages} isTyping={isTyping || isSendingReflection}>
        {showMoodSelector && (
          <MoodSelector onSelect={handleMoodSelect} disabled={isSavingMood} />
        )}
      </ChatMessageList>
      {showReflectionInput && (
        <ReflectionInput onSubmit={handleReflectionSubmit} disabled={isSendingReflection} />
      )}
    </div>
  );
}
