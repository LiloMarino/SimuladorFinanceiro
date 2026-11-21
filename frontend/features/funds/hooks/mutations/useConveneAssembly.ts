import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundAssemblyConveneRequest } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** Convoca a assembleia de troca de gestor, indicando o próprio convocador ou um aliado. */
export function useConveneAssembly(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundAssemblyConveneRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/assembly`, { method: "POST", body: request }),
    onSettled: () => void queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
