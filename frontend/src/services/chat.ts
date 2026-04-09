import { apiRequest } from "./api";
import type { DailyChat, MonthlyChat, Mood } from "../types/api";

export async function getTodayChat(localDate: string): Promise<DailyChat> {
  return apiRequest<DailyChat>(`/chats/today/?date=${localDate}`);
}

export async function patchChatMood(chatId: number, mood: Mood): Promise<DailyChat> {
  return apiRequest<DailyChat>(`/chats/${chatId}/`, {
    method: "PATCH",
    body: { mood },
  });
}

export async function patchChatReflection(chatId: number, userResponse: string): Promise<DailyChat> {
  return apiRequest<DailyChat>(`/chats/${chatId}/`, {
    method: "PATCH",
    body: { user_response: userResponse },
  });
}

export async function getChatById(chatId: number): Promise<DailyChat> {
  return apiRequest<DailyChat>(`/chats/${chatId}/`);
}

export async function getMonthlyChats(year: number, month: number): Promise<MonthlyChat[]> {
  return apiRequest<MonthlyChat[]>(`/chats/monthly/?year=${year}&month=${month}`);
}
