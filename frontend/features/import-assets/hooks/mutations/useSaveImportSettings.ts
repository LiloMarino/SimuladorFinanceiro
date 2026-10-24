import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ImportSettings } from "@/types";

export function useSaveImportSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (settings: ImportSettings) =>
      apiFetch<ImportSettings>("/api/import-assets/settings", { method: "PUT", body: settings }),
    onSuccess: (saved) => queryClient.setQueryData(queryKeys.importSettings(), saved),
    onError: (err) => toastApiError(err),
  });
}
