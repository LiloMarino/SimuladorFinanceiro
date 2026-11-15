import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ProposeMeasureRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useProposeMeasure() {
  const queryClient = useQueryClient();
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: ProposeMeasureRequest) => apiFetch("/api/government/measures", { method: "POST", body }),
    onSuccess: () => {
      renew();
      // Fundar e privatizar mexem na tabela das estatais: a linha ganha o selo de votação
      void queryClient.invalidateQueries({ queryKey: queryKeys.stateCompanies() });
    },
  });
}
