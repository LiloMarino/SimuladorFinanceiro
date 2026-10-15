import { createContext } from "react";
import type ApiError from "@/shared/lib/models/ApiError";
import type { NotificationPreferences } from "@/types";

export type NotificationSettingsContextType = {
  preferences: NotificationPreferences;
  /** Sem salvar, o valor volta ao anterior e `onError` diz o que houve a quem mudou */
  updatePreferences: (prefs: NotificationPreferences, options?: { onError?: (err: ApiError) => void }) => void;
};

export const NotificationSettingsContext = createContext<NotificationSettingsContextType | null>(null);
