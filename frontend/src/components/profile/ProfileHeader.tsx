import type { User } from "../../types/api";
import "./ProfileHeader.css";

interface ProfileHeaderProps {
  user: User;
}

function formatJoinDate(isoDate: string): string {
  const date = new Date(isoDate);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default function ProfileHeader({ user }: ProfileHeaderProps) {
  return (
    <div className="profile-header">
      <div className="profile-header__avatar">{user.avatar_emoji}</div>
      <h2 className="profile-header__name">{user.display_name}</h2>
      <p className="profile-header__joined">
        Member since {formatJoinDate(user.date_joined)}
      </p>
    </div>
  );
}
