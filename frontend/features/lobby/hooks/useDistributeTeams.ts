import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** O host põe cada jogador sem equipe na equipe com menos gente. */
export function useDistributeTeams() {
  return useApiMutation({
    mutationFn: () => apiFetch<void>("/api/simulation/teams/distribute", { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
