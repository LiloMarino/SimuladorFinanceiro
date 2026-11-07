import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PortfolioDividends } from "@/types";

/**
 * Proventos recebidos na partida: total, últimos 12 meses, barras por mês e por ano
 * e quem mais pagou. Renovado quando a carteira é invalidada (aviso de provento).
 */
export function usePortfolioDividends() {
  return useQuery({
    queryKey: queryKeys.portfolioDividends(),
    queryFn: ({ signal }) => apiFetch<PortfolioDividends>("/api/portfolio/dividends", { signal }),
  });
}
