import { apiRequest } from "./api";
import type { ProfileStats } from "../types/api";

export async function getProfileStats(): Promise<ProfileStats> {
  return apiRequest<ProfileStats>("/profile/stats/");
}
