import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { TreasuryCover } from "@/types";

export function useSetTreasuryCover() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: TreasuryCover) =>
      apiFetch<TreasuryCover>("/api/settings/treasury-cover", { method: "PUT", body }),
    onSuccess: (cover) => {
      queryClient.setQueryData(queryKeys.treasuryCover(), cover);
      void queryClient.invalidateQueries({ queryKey: queryKeys.lifeStatusAll() });
    },
    onError: (err) => toastApiError(err),
  });
}
