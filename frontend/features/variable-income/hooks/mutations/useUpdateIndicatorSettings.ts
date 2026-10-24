import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { IndicatorSettings, UserSettings } from "@/types";

/**
 * Grava os indicadores nas configurações do jogador. O PUT grava as configurações
 * inteiras, então o corpo é o cache atual com os indicadores novos; a chave de
 * mutação é a mesma das notificações, e as duas se enxergam no rollback.
 */
export function useUpdateIndicatorSettings() {
  const queryClient = useQueryClient();
  const key = queryKeys.userSettings();

  return useMutation({
    mutationKey: key,
    mutationFn: (indicators: IndicatorSettings) => {
      const current = queryClient.getQueryData<UserSettings>(key);
      return apiFetch<UserSettings>("/api/settings", { method: "PUT", body: { ...current, indicators } });
    },

    // O gráfico redesenha na hora: o valor otimista entra no cache antes da resposta
    onMutate: async (indicators) => {
      await queryClient.cancelQueries({ queryKey: key });
      const previous = queryClient.getQueryData<UserSettings>(key);
      if (previous) queryClient.setQueryData<UserSettings>(key, { ...previous, indicators });
      return { previous };
    },

    // Desfaz só se esta for a última mutação em voo: a mais recente manda no cache
    onError: (_err, _indicators, context) => {
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
