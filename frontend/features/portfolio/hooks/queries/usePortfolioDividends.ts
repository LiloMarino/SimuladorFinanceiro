import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PortfolioDividends } from "@/types";

/**
 * Proventos recebidos na partida pelo jogador: total, últimos 12 meses, barras por mês e por ano
 * e quem mais pagou. O aviso de provento (`corporate_actions`) relê a consulta.
 */
export function usePortfolioDividends() {
  return useQuery({
    queryKey: queryKeys.portfolioDividends("personal"),
    queryFn: ({ signal }) => apiFetch<PortfolioDividends>("/api/portfolio/dividends", { signal }),
  });
}
