import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { FundDetails } from "@/types";
import { fundKeys } from "../fund-keys";

/** A página de uma gestora; a carteira posição a posição só vem para o gestor. Quando algo muda (funds_update), busca de novo. */
export function useFund(fundId: number) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: fundKeys.detail(fundId),
    queryFn: ({ signal }) => apiFetch<FundDetails>(`/api/funds/${fundId}`, { signal }),
  });

  useRealtime("funds_update", () => {
    void queryClient.invalidateQueries({ queryKey: fundKeys.all() });
  });

  return query;
}
