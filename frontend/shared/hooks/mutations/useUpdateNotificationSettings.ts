import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { NotificationPreferences } from "@/types";

export function useUpdateNotificationSettings() {
  const queryClient = useQueryClient();

  return useMutation({
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
    onError: (_err, _next, context) => {
      if (queryClient.isMutating({ mutationKey: queryKeys.notificationSettings() }) === 1) {
        queryClient.setQueryData(queryKeys.notificationSettings(), context?.previous);
      }
    },

    onSettled: () => {
      if (queryClient.isMutating({ mutationKey: queryKeys.notificationSettings() }) === 1) {
        void queryClient.invalidateQueries({ queryKey: queryKeys.notificationSettings() });
      }
    },
  });
}
