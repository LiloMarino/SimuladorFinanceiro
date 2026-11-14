import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundSummary } from "@/types";
import { fundKeys } from "../fund-keys";

// Preço e patrimônio por cota andam com o pregão e não chegam por tempo real: a lista se renova sozinha
const REFRESH_MS = 10_000;

/** As gestoras da partida, cada uma com o patrimônio por cota de agora e o preço de ranking. */
export function useFunds({ enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: fundKeys.list(),
    queryFn: ({ signal }) => apiFetch<FundSummary[]>("/api/funds", { signal }),
    enabled,
    refetchInterval: REFRESH_MS,
  });
}
