import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";

export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>("/api/session/logout", { method: "POST", body: {} }),
    onSuccess: () => queryClient.setQueryData(queryKeys.authSession(), null),
  });
}
