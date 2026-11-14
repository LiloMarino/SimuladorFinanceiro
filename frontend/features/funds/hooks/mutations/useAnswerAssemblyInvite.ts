import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { fundKeys } from "../fund-keys";

/** O aliado indicado aceita (a votação abre) ou recusa o convite. */
export function useAnswerAssemblyInvite(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accept: boolean) =>
      apiFetch<void>(`/api/funds/${fundId}/assembly/${accept ? "acceptance" : "refusal"}`, { method: "POST" }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
