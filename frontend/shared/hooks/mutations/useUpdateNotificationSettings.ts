import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { NotificationSettings, UserSettings } from "@/types";

/**
 * Grava as notificações nas configurações do jogador. O PUT grava as configurações
 * inteiras, então o corpo é o cache atual com as notificações novas; a chave de
 * mutação é a mesma dos indicadores, e as duas se enxergam no rollback.
 */
export function useUpdateNotificationSettings() {
  const queryClient = useQueryClient();
  const key = queryKeys.userSettings();

  return useMutation({
    mutationKey: key,
    mutationFn: (notifications: NotificationSettings) => {
      const current = queryClient.getQueryData<UserSettings>(key);
      return apiFetch<UserSettings>("/api/settings", { method: "PUT", body: { ...current, notifications } });
    },

    // UX instantâneo: escreve o valor otimista no cache antes da resposta do PUT.
    onMutate: async (notifications) => {
      await queryClient.cancelQueries({ queryKey: key });
      const previous = queryClient.getQueryData<UserSettings>(key);
      if (previous) queryClient.setQueryData<UserSettings>(key, { ...previous, notifications });
      return { previous };
    },

    // Se o PUT falhar, desfaz o valor otimista, mas só se essa for a última
    // mutação em voo: se o usuário já disparou outra mudança depois desta, é
    // ela quem manda no cache, e o rollback desta não atropela a mais recente.
    onError: (_err, _next, context) => {
      if (queryClient.isMutating({ mutationKey: key }) === 1) {
        queryClient.setQueryData(key, context?.previous);
      }
    },

    onSettled: () => {
      if (queryClient.isMutating({ mutationKey: key }) === 1) {
        void queryClient.invalidateQueries({ queryKey: key });
      }
    },
  });
}
