import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyParamValue } from "@/types";

type SaveStrategyParams = { key: string; params: Record<string, StrategyParamValue> };

/** Grava no perfil os parâmetros de uma estratégia, que o automático usa em toda partida. */
export function useSaveStrategyParams() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ key, params }: SaveStrategyParams) =>
      apiFetch<Record<string, StrategyParamValue>>(`/api/settings/strategy-params/${key}`, {
        method: "PUT",
        body: params,
      }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: queryKeys.savedStrategyParams() }),
  });
}
