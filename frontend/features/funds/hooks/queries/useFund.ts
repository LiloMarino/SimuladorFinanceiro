import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundDetails } from "@/types";
import { fundKeys } from "../fund-keys";

// A carteira, os cotistas e o preço andam com o pregão e não chegam por tempo real: a página se renova sozinha
const REFRESH_MS = 10_000;

/** A página de uma gestora; a carteira posição a posição só vem para o gestor. */
export function useFund(fundId: number) {
  return useQuery({
    queryKey: fundKeys.detail(fundId),
    queryFn: ({ signal }) => apiFetch<FundDetails>(`/api/funds/${fundId}`, { signal }),
    refetchInterval: REFRESH_MS,
  });
}
