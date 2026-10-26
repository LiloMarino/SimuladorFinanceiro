import { useCallback } from "react";
import type { PropsWithChildren } from "react";
import { NotificationSettingsContext } from "./NotificationSettingsContext";
import { useNotificationSettings } from "@/shared/hooks/queries/useNotificationSettings";
import { useUpdateNotificationSettings } from "@/shared/hooks/mutations/useUpdateNotificationSettings";
import type ApiError from "@/shared/lib/models/ApiError";
import type { NotificationPreferences } from "@/types";

const DEFAULT_PREFERENCES: NotificationPreferences = {
  orders: {
    executed: true,
    partial: true,
  },
  players: {
    join_exit: true,
  },
};

export function NotificationSettingsProvider({ children }: PropsWithChildren) {
  const { data } = useNotificationSettings();

  const preferences: NotificationPreferences = { ...DEFAULT_PREFERENCES, ...(data ?? {}) };

  const updateMutation = useUpdateNotificationSettings();

  const updatePreferences = useCallback(
    (next: NotificationPreferences, options?: { onError?: (err: ApiError) => void }) => {
      updateMutation.mutate(next, options?.onError ? { onError: options.onError } : {});
    },
    [updateMutation],
  );

  return (
    <NotificationSettingsContext.Provider
      value={{
        preferences,
        updatePreferences,
      }}
    >
      {children}
    </NotificationSettingsContext.Provider>
  );
}
