import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ProposeMeasureRequest } from "@/types";

export function useProposeMeasure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: ProposeMeasureRequest) => apiFetch("/api/government/measures", { method: "POST", body }),
    onSuccess: () => {
      // Fundar e privatizar mexem na tabela das estatais: a linha ganha o selo de votação
      void queryClient.invalidateQueries({ queryKey: queryKeys.stateCompanies() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.sovereignFund() });
    },
  });
}
