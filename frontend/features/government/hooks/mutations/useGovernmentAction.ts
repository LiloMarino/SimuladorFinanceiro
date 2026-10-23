import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { GovernmentAction, GovernmentView } from "@/types";
import { governmentRequestId } from "../../lib/request-id";
import { revalidateGovernmentImpact } from "@/shared/lib/simulation-cache";

export function useGovernmentAction() {
  const client = useQueryClient();
  const { simulation } = useSimulation();
  return useMutation({
    mutationFn: (body: GovernmentAction) => apiFetch<GovernmentView>("/api/government/actions", { method: "POST", body: { ...body, request_id: body.request_id ?? governmentRequestId() } }),
    retry: false,
    onSuccess: (data) => {
      client.setQueryData(queryKeys.government(simulation?.simulation?.id ?? 0), data);
      void revalidateGovernmentImpact(client);
    },
    onError: err => toastApiError(err),
  });
}
