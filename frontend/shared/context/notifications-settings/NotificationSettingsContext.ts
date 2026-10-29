import { createContext } from "react";
import type ApiError from "@/shared/lib/models/ApiError";
import type { NotificationSettings, ToastType } from "@/types";

export type NotificationSettingsContextType = {
  /** Indefinido enquanto as configurações do jogador não chegaram */
  preferences: NotificationSettings | undefined;
  /** Se o aviso do tipo sobe como toast; sem as configurações, sobe */
  isToastOn: (type: ToastType) => boolean;
  /** Sem salvar, o valor volta ao anterior e `onError` diz o que houve a quem mudou */
  updatePreferences: (prefs: NotificationSettings, options?: { onError?: (err: ApiError) => void }) => void;
};

export const NotificationSettingsContext = createContext<NotificationSettingsContextType | null>(null);
