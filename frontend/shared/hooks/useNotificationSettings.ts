import { useContext } from "react";
import { NotificationSettingsContext } from "@/shared/context/notifications-settings";

export function useNotificationSettings() {
  const ctx = useContext(NotificationSettingsContext);
  if (!ctx) {
    throw new Error("useNotificationSettings must be used within NotificationSettingsProvider");
  }
  return ctx;
}
