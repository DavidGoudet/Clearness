import type { ProfileStats } from "../../types/api";
import "./StatsGrid.css";

interface StatsGridProps {
  stats: ProfileStats;
}

export default function StatsGrid({ stats }: StatsGridProps) {
  const mood = stats.most_frequent_mood;

  return (
    <div className="stats-grid">
      <div className="stats-grid__card">
        <span className="stats-grid__icon">💬</span>
        <span className="stats-grid__value">{stats.total_chats}</span>
        <span className="stats-grid__label">Total Chats</span>
      </div>
      <div className="stats-grid__card">
        <span className="stats-grid__icon">🔥</span>
        <span className="stats-grid__value">{stats.current_streak}</span>
        <span className="stats-grid__label">Current Streak</span>
      </div>
      <div className="stats-grid__card">
        <span className="stats-grid__icon">
          {mood ? mood.emoji : "🤔"}
        </span>
        <span className="stats-grid__value">
          {mood ? mood.label : "None yet"}
        </span>
        <span className="stats-grid__label">Top Mood</span>
      </div>
      <div className="stats-grid__card">
        <span className="stats-grid__icon">⭐</span>
        <span className="stats-grid__value">{stats.longest_streak}</span>
        <span className="stats-grid__label">Longest Streak</span>
      </div>
    </div>
  );
}
