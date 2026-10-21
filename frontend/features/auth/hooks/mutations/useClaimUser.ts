import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { User, UserClaimRequest } from "@/types";

export function useClaimUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: UserClaimRequest) => apiFetch<User>("/api/user/claim", { method: "POST", body }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.authSession() }),
  });
}
