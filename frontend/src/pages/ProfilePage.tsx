import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import type { ProfileStats } from "../types/api";
import { getProfileStats } from "../services/profile";
import ProfileHeader from "../components/profile/ProfileHeader";
import StatsGrid from "../components/profile/StatsGrid";
import "./ProfilePage.css";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState<ProfileStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getProfileStats();
      setStats(data);
    } catch {
      setError("Could not load your journey stats.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (!user) return null;

  return (
    <div className="page profile-page">
      <ProfileHeader user={user} />

      <h3 className="profile-page__section-title">Your Journey</h3>

      {isLoading && (
        <div className="profile-page__loading">Loading stats...</div>
      )}
      {error && <div className="profile-page__error">{error}</div>}
      {!isLoading && !error && stats && <StatsGrid stats={stats} />}

      <button className="profile-page__signout" onClick={logout}>
        Sign Out
      </button>
    </div>
  );
}
