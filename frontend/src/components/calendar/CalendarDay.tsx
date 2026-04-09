import type { MoodOption } from "../../constants/moods";

interface CalendarDayProps {
  day: number;
  mood: MoodOption | null;
  isToday: boolean;
  onClick?: (day: number) => void;
}

export default function CalendarDay({ day, mood, isToday, onClick }: CalendarDayProps) {
  let className = "calendar-day";
  if (isToday) className += " calendar-day--today";
  if (mood) className += " calendar-day--has-mood";

  return (
    <div
      className={className}
      onClick={() => onClick?.(day)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") onClick?.(day);
      }}
      role="button"
      tabIndex={0}
      style={{ cursor: "pointer" }}
    >
      <span className="calendar-day__number">{day}</span>
      {mood && <span className="calendar-day__emoji">{mood.emoji}</span>}
    </div>
  );
}
