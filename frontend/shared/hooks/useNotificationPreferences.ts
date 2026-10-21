import { useContext } from "react";
import { NotificationSettingsContext } from "@/shared/context/notifications-settings";

export function useNotificationPreferences() {
  const ctx = useContext(NotificationSettingsContext);
  if (!ctx) {
    throw new Error("useNotificationPreferences must be used within NotificationSettingsProvider");
  }
  return ctx;
}
