export interface User {
  id: number;
  email: string;
  display_name: string;
  avatar_emoji: string;
  timezone: string;
  date_joined: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface TokenRefreshResponse {
  access: string;
}

export interface ChatMessage {
  id: number;
  sender: "bot" | "user";
  message_type:
    | "greeting"
    | "mood_prompt"
    | "mood_response"
    | "reflection_prompt"
    | "reflection_response"
    | "acknowledgment";
  content: string;
  order: number;
  created_at: string;
}

export type Mood = "happy" | "calm" | "neutral" | "down" | "frustrated";

export interface MonthlyChat {
  id: number;
  date: string;
  mood: Mood;
}

export interface MoodDetail {
  value: Mood;
  emoji: string;
  label: string;
}

export interface ProfileStats {
  total_chats: number;
  current_streak: number;
  longest_streak: number;
  most_frequent_mood: MoodDetail | null;
}

export interface DailyChat {
  id: number;
  date: string;
  mood: Mood | "";
  status: "in_progress" | "completed";
  started_at: string;
  completed_at: string | null;
  messages: ChatMessage[];
}
