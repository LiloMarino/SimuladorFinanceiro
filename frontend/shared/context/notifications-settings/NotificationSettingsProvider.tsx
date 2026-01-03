import { useState } from "react";
import type { PropsWithChildren } from "react";
import { NotificationSettingsContext } from "./NotificationSettingsContext";
import type { NotificationPreferences } from "@/types";

const DEFAULT_PREFERENCES: NotificationPreferences = {
  orders: {
    executed: true,
    partial: true,
  },
};

export function NotificationSettingsProvider({ children }: PropsWithChildren) {
  const [preferences, setPreferences] = useState<NotificationPreferences>(DEFAULT_PREFERENCES);

  return (
    <NotificationSettingsContext.Provider
      value={{
        preferences,
        updatePreferences: setPreferences,
      }}
    >
      {children}
    </NotificationSettingsContext.Provider>
  );
}
