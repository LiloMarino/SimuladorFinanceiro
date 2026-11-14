import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FundIdentity } from "@/types";

/** Grava nome e sigla da gestora no perfil do jogador. */
export function useSaveMyFund() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: FundIdentity) => apiFetch<FundIdentity>("/api/settings/fund", { method: "PUT", body }),
    onSuccess: (saved) => queryClient.setQueryData(queryKeys.myFund(), saved),
  });
}
