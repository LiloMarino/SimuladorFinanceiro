import { useEffect, useState, useCallback } from "react";
import type { PropsWithChildren } from "react";
import { NotificationSettingsContext } from "./NotificationSettingsContext";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import type { NotificationPreferences } from "@/types";
import { toast } from "sonner";

const DEFAULT_PREFERENCES: NotificationPreferences = {
  orders: {
    executed: true,
    partial: true,
  },
};

export function NotificationSettingsProvider({ children }: PropsWithChildren) {
  const [preferences, setPreferences] = useState<NotificationPreferences>(DEFAULT_PREFERENCES);
  const { data } = useQueryApi<NotificationPreferences>("/api/settings");
  const { mutate } = useMutationApi<NotificationPreferences, NotificationPreferences>("/api/settings", {
    method: "PUT",
    onError: (err) => {
      toast.error(err.message);
    },
  });

  // 🔹 Sincroniza backend → frontend
  useEffect(() => {
    if (data) {
      setPreferences({
        ...DEFAULT_PREFERENCES,
        ...data, // backend sobrescreve defaults
      });
    }
  }, [data]);

  // 🔹 Atualiza frontend + backend
  const updatePreferences = useCallback(
    (next: NotificationPreferences) => {
      setPreferences(next); // UX instantâneo
      mutate(next); // Persiste
    },
    [mutate]
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
