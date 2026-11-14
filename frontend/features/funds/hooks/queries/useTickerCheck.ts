import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundTickerCheck } from "@/types";
import { fundKeys } from "../fund-keys";

/** A conferência da sigla no servidor: livre, fora do formato, de um ativo ou de outra gestora. */
export function useTickerCheck(ticker: string, { enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: fundKeys.tickerCheck(ticker),
    queryFn: ({ signal }) =>
      apiFetch<FundTickerCheck>(`/api/funds/ticker-check?ticker=${encodeURIComponent(ticker)}`, { signal }),
    enabled,
    staleTime: 0,
  });
}
