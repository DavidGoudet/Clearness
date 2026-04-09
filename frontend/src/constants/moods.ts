import type { Mood } from "../types/api";

export interface MoodOption {
  value: Mood;
  emoji: string;
  label: string;
}

export const MOOD_OPTIONS: MoodOption[] = [
  { value: "happy", emoji: "😊", label: "Happy" },
  { value: "calm", emoji: "😌", label: "Calm" },
  { value: "neutral", emoji: "😐", label: "Neutral" },
  { value: "down", emoji: "😔", label: "Down" },
  { value: "frustrated", emoji: "😤", label: "Frustrated" },
];
