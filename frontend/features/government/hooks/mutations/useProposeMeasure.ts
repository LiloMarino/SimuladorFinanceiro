import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { ProposeMeasureRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useProposeMeasure() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: ProposeMeasureRequest) => apiFetch("/api/government/measures", { method: "POST", body }),
    onSuccess: renew,
  });
}
