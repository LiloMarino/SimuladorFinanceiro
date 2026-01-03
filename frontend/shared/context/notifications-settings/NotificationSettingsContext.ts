import { createContext } from "react";
import type { NotificationPreferences } from "@/types";

export type NotificationSettingsContextType = {
  preferences: NotificationPreferences;
  updatePreferences: (prefs: NotificationPreferences) => void;
};

export const NotificationSettingsContext = createContext<NotificationSettingsContextType | null>(null);
