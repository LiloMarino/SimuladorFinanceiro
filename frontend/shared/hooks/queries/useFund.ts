import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FundDetails } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** A página de uma gestora; a carteira posição a posição só vem para o gestor. Quando algo muda, o servidor entrega a página nova por `fund_update:{id}`. */
export function useFund(fundId: number) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: fundKeys.detail(fundId),
    queryFn: ({ signal }) => apiFetch<FundDetails>(`/api/funds/${fundId}`, { signal }),
    staleTime: 0,
  });

  useRealtime(`fund_update:${fundId}`, (details) => {
    void applyRealtime<FundDetails>(queryClient, fundKeys.detail(fundId), details);
  });

  return query;
}
