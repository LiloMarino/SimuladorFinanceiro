import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundAssemblyVoteRequest } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O cotista vota a favor ou contra uma pauta e muda o voto até o fim da votação. */
export function useCastAssemblyVote(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundAssemblyVoteRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/assembly/vote`, { method: "PUT", body: request }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
