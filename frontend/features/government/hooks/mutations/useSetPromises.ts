import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { PromisesRequest } from "@/types";

export function useSetPromises() {
  return useMutation({
    mutationFn: (body: PromisesRequest) => apiFetch("/api/government/promises", { method: "PUT", body }),
    onError: (err) => toastApiError(err),
  });
}
