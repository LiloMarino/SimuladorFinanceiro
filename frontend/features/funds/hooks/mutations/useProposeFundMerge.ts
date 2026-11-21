import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundMergeProposalRequest } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O gestor das duas gestoras leva a fusão à assembleia de cada uma; `fundId` é a que incorpora. */
export function useProposeFundMerge(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundMergeProposalRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/assembly/merge`, { method: "POST", body: request }),
    onSettled: () => void queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
