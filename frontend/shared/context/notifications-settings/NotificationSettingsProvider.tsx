import { useCallback } from "react";
import type { PropsWithChildren } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { NotificationSettingsContext } from "./NotificationSettingsContext";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { NotificationPreferences } from "@/types";
import { toast } from "sonner";

const DEFAULT_PREFERENCES: NotificationPreferences = {
  orders: {
    executed: true,
    partial: true,
  },
};

export function NotificationSettingsProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();

  const { data } = useApiQuery({
    queryKey: queryKeys.notificationSettings(),
    queryFn: ({ signal }) => apiFetch<NotificationPreferences>("/api/settings", { signal }),
  });

  const preferences: NotificationPreferences = { ...DEFAULT_PREFERENCES, ...(data ?? {}) };

  const updateMutation = useApiMutation({
    mutationKey: queryKeys.notificationSettings(),
    mutationFn: (next: NotificationPreferences) =>
      apiFetch<NotificationPreferences>("/api/settings", { method: "PUT", body: next }),

    // UX instantâneo: escreve o valor otimista no cache antes da resposta do PUT.
    onMutate: async (next) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.notificationSettings() });
      const previous = queryClient.getQueryData<NotificationPreferences>(queryKeys.notificationSettings());
      queryClient.setQueryData(queryKeys.notificationSettings(), next);
      return { previous };
    },

    // Se o PUT falhar, desfaz o valor otimista — mas só se essa for a última
    // mutação em voo: se o usuário já disparou outra mudança depois desta, é
    // ela quem manda no cache, e não deixamos o rollback desta atropelar o
    // sucesso da mais recente (ver "Concurrent Optimistic Updates" do TkDodo).
    onError: (err, _next, context) => {
      if (queryClient.isMutating({ mutationKey: queryKeys.notificationSettings() }) === 1) {
        queryClient.setQueryData(queryKeys.notificationSettings(), context?.previous);
      }
      toast.error(err.message);
    },

    onSettled: () => {
      if (queryClient.isMutating({ mutationKey: queryKeys.notificationSettings() }) === 1) {
        queryClient.invalidateQueries({ queryKey: queryKeys.notificationSettings() });
      }
    },
  });

  const updatePreferences = useCallback(
    (next: NotificationPreferences) => {
      updateMutation.mutate(next);
    },
    [updateMutation]
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
