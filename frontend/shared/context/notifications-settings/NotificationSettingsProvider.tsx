import { useCallback } from "react";
import type { PropsWithChildren } from "react";
import { NotificationSettingsContext } from "./NotificationSettingsContext";
import { useNotificationSettings } from "@/shared/hooks/queries/useNotificationSettings";
import { useUpdateNotificationSettings } from "@/shared/hooks/mutations/useUpdateNotificationSettings";
import type ApiError from "@/shared/lib/models/ApiError";
import type { NotificationSettings, ToastType } from "@/types";

export function NotificationSettingsProvider({ children }: PropsWithChildren) {
  const { data: preferences } = useNotificationSettings();

  const updateMutation = useUpdateNotificationSettings();

  const updatePreferences = useCallback(
    (next: NotificationSettings, options?: { onError?: (err: ApiError) => void }) => {
      updateMutation.mutate(next, options?.onError ? { onError: options.onError } : {});
    },
    [updateMutation],
  );

  const isToastOn = (type: ToastType) => preferences?.toasts[type] ?? true;

  return (
    <NotificationSettingsContext.Provider value={{ preferences, isToastOn, updatePreferences }}>
      {children}
    </NotificationSettingsContext.Provider>
  );
}
