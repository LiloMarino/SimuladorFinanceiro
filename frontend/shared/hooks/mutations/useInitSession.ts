import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Session } from "@/types";

/** Abre uma sessão nova, com client_id novo. */
export function useInitSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<Session>("/api/session/init", { method: "POST", body: {} }),
    onSuccess: (data) => queryClient.setQueryData(queryKeys.authSession(), data),
  });
}
