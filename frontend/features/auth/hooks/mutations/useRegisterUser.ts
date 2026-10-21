import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { User, UserRegisterRequest } from "@/types";

export function useRegisterUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: UserRegisterRequest) => apiFetch<User>("/api/user/register", { method: "POST", body }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.authSession() }),
  });
}
