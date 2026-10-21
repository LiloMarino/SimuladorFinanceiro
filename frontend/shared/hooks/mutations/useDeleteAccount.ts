import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";

export function useDeleteAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>("/api/user", { method: "DELETE" }),
    onSuccess: () => queryClient.setQueryData(queryKeys.authSession(), null),
  });
}
