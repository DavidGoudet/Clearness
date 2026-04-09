import type { MoodOption } from "../../constants/moods";
import CalendarDay from "./CalendarDay";
import "./CalendarGrid.css";

const DAY_HEADERS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

interface CalendarGridProps {
  year: number;
  month: number;
  moodByDay: Map<number, MoodOption>;
  today: { year: number; month: number; day: number };
  onDayClick?: (day: number) => void;
}

export default function CalendarGrid({ year, month, moodByDay, today, onDayClick }: CalendarGridProps) {
  const firstDayOfWeek = new Date(year, month - 1, 1).getDay();
  const daysInMonth = new Date(year, month, 0).getDate();

  const isCurrentMonth = today.year === year && today.month === month;

  const emptyCells = Array.from({ length: firstDayOfWeek }, (_, i) => (
    <div key={`empty-${i}`} className="calendar-grid__empty-cell" />
  ));

  const dayCells = Array.from({ length: daysInMonth }, (_, i) => {
    const day = i + 1;
    return (
      <CalendarDay
        key={day}
        day={day}
        mood={moodByDay.get(day) ?? null}
        isToday={isCurrentMonth && today.day === day}
        onClick={onDayClick}
      />
    );
  });

  return (
    <div className="calendar-grid">
      {DAY_HEADERS.map((header) => (
        <div key={header} className="calendar-grid__header">
          {header}
        </div>
      ))}
      {emptyCells}
      {dayCells}
    </div>
  );
}
