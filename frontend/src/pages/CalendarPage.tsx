import { useCallback, useEffect, useState } from "react";
import type { DailyChat, MonthlyChat } from "../types/api";
import type { MoodOption } from "../constants/moods";
import { MOOD_OPTIONS } from "../constants/moods";
import { getChatById, getMonthlyChats } from "../services/chat";
import CalendarGrid from "../components/calendar/CalendarGrid";
import DaySummaryModal from "../components/calendar/DaySummaryModal";
import "./CalendarPage.css";

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const moodMap = new Map<string, MoodOption>(
  MOOD_OPTIONS.map((m) => [m.value, m])
);

function buildMoodByDay(chats: MonthlyChat[]): Map<number, MoodOption> {
  const result = new Map<number, MoodOption>();
  for (const chat of chats) {
    const dayStr = chat.date.split("-")[2];
    if (!dayStr) continue;
    const day = parseInt(dayStr, 10);
    const mood = moodMap.get(chat.mood);
    if (mood) result.set(day, mood);
  }
  return result;
}

function buildChatIdByDay(chats: MonthlyChat[]): Map<number, number> {
  const result = new Map<number, number>();
  for (const chat of chats) {
    const dayStr = chat.date.split("-")[2];
    if (!dayStr) continue;
    const day = parseInt(dayStr, 10);
    result.set(day, chat.id);
  }
  return result;
}

function getToday() {
  const now = new Date();
  return { year: now.getFullYear(), month: now.getMonth() + 1, day: now.getDate() };
}

export default function CalendarPage() {
  const today = getToday();
  const [year, setYear] = useState(today.year);
  const [month, setMonth] = useState(today.month);
  const [moodByDay, setMoodByDay] = useState<Map<number, MoodOption>>(new Map());
  const [chatIdByDay, setChatIdByDay] = useState<Map<number, number>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [selectedChat, setSelectedChat] = useState<DailyChat | null>(null);
  const [isSummaryLoading, setIsSummaryLoading] = useState(false);

  const fetchMonthData = useCallback(async (y: number, m: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const chats = await getMonthlyChats(y, m);
      setMoodByDay(buildMoodByDay(chats));
      setChatIdByDay(buildChatIdByDay(chats));
    } catch {
      setError("Could not load calendar data.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMonthData(year, month);
  }, [year, month, fetchMonthData]);

  const handleDayClick = useCallback(async (day: number) => {
    setSelectedDay(day);
    const chatId = chatIdByDay.get(day);
    if (!chatId) {
      setSelectedChat(null);
      return;
    }
    setIsSummaryLoading(true);
    try {
      const chat = await getChatById(chatId);
      setSelectedChat(chat);
    } catch {
      setSelectedChat(null);
    } finally {
      setIsSummaryLoading(false);
    }
  }, [chatIdByDay]);

  const handleCloseModal = useCallback(() => {
    setSelectedDay(null);
    setSelectedChat(null);
  }, []);

  const goToPreviousMonth = () => {
    if (month === 1) {
      setYear((y) => y - 1);
      setMonth(12);
    } else {
      setMonth((m) => m - 1);
    }
  };

  const goToNextMonth = () => {
    if (month === 12) {
      setYear((y) => y + 1);
      setMonth(1);
    } else {
      setMonth((m) => m + 1);
    }
  };

  const selectedDate = selectedDay
    ? { year, month, day: selectedDay }
    : null;

  return (
    <div className="page calendar-page">
      <div className="calendar-page__nav">
        <button className="calendar-page__arrow" onClick={goToPreviousMonth} aria-label="Previous month">
          &lsaquo;
        </button>
        <h2 className="calendar-page__title">
          {MONTH_NAMES[month - 1]} {year}
        </h2>
        <button className="calendar-page__arrow" onClick={goToNextMonth} aria-label="Next month">
          &rsaquo;
        </button>
      </div>

      {isLoading && <div className="calendar-page__loading">Loading...</div>}
      {error && <div className="calendar-page__error">{error}</div>}
      {!isLoading && !error && (
        <CalendarGrid
          year={year}
          month={month}
          moodByDay={moodByDay}
          today={today}
          onDayClick={handleDayClick}
        />
      )}

      <DaySummaryModal
        selectedDate={selectedDate}
        chat={selectedChat}
        isLoading={isSummaryLoading}
        onClose={handleCloseModal}
      />
    </div>
  );
}
