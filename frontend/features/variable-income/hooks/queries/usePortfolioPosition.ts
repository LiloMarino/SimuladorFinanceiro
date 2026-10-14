import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { Position } from "@/types";

/**
 * Posição do jogador num ticker, mantida viva via position_update:{ticker} (a cada
 * execução) e portfolio_update (valor e retorno no preço do tick).
 */
export function usePortfolioPosition(ticker: string | undefined) {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.portfolioPosition(ticker ?? ""),
    queryFn: ({ signal }) => apiFetch<Position>(`/api/portfolio/${ticker}`, { signal }),
    enabled: !!ticker,
  });

  useRealtime(
    `position_update:${ticker}`,
    ({ position }) => {
      queryClient.setQueryData(queryKeys.portfolioPosition(ticker ?? ""), position);
    },
    !!ticker,
  );

  useRealtime(
    "portfolio_update",
    ({ portfolio }) => {
      const position = portfolio.variable_income.find((p) => p.ticker === ticker);
      if (position) {
        queryClient.setQueryData(queryKeys.portfolioPosition(ticker ?? ""), position);
      }
    },
    !!ticker,
  );

  return query;
}
