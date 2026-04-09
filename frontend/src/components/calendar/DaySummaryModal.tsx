import { useEffect } from "react";
import type { DailyChat } from "../../types/api";
import type { MoodOption } from "../../constants/moods";
import { MOOD_OPTIONS } from "../../constants/moods";
import "./DaySummaryModal.css";

const moodMap = new Map<string, MoodOption>(
  MOOD_OPTIONS.map((m) => [m.value, m])
);

interface DaySummaryModalProps {
  selectedDate: { year: number; month: number; day: number } | null;
  chat: DailyChat | null;
  isLoading: boolean;
  onClose: () => void;
}

function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function getReflectionText(chat: DailyChat): string | null {
  const msg = chat.messages.find(
    (m) => m.message_type === "reflection_response" && m.sender === "user"
  );
  return msg?.content ?? null;
}

export default function DaySummaryModal({
  selectedDate,
  chat,
  isLoading,
  onClose,
}: DaySummaryModalProps) {
  useEffect(() => {
    if (!selectedDate) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [selectedDate, onClose]);

  if (!selectedDate) return null;

  const mood = chat ? moodMap.get(chat.mood) : null;
  const reflection = chat ? getReflectionText(chat) : null;

  return (
    <div className="day-summary-backdrop" onClick={onClose}>
      <div
        className="day-summary-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Day summary"
      >
        <button
          className="day-summary-modal__close"
          onClick={onClose}
          aria-label="Close"
        >
          &times;
        </button>

        <h3 className="day-summary-modal__date">
          {selectedDate.month}/{selectedDate.day}/{selectedDate.year}
        </h3>

        {isLoading && (
          <p className="day-summary-modal__loading">Loading...</p>
        )}

        {!isLoading && !chat && (
          <p className="day-summary-modal__empty">No entry for this day</p>
        )}

        {!isLoading && chat && mood && (
          <div className="day-summary-modal__content">
            <span className="day-summary-modal__emoji">{mood.emoji}</span>
            <span className="day-summary-modal__label">{mood.label}</span>

            {reflection && (
              <p className="day-summary-modal__reflection">{reflection}</p>
            )}

            {chat.completed_at && (
              <p className="day-summary-modal__timestamp">
                Completed {formatTimestamp(chat.completed_at)}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
