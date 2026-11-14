import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { eventAccountKey } from "@/shared/lib/active-account";
import type { Position } from "@/types";

/**
 * Posição da conta ativa num ticker, mantida viva via position_update:{ticker} (a cada
 * execução) e portfolio_update (valor e retorno no preço do tick).
 */
export function usePortfolioPosition(ticker: string | undefined) {
  const queryClient = useQueryClient();
  const { accountKey } = useActiveAccount();

  const query = useQuery({
    queryKey: queryKeys.portfolioPosition(accountKey, ticker ?? ""),
    queryFn: ({ signal }) => apiFetch<Position>(`/api/portfolio/${ticker}`, { signal, activeAccount: true }),
    enabled: !!ticker,
  });

  useRealtime(
    `position_update:${ticker}`,
    ({ position, account }) => {
      queryClient.setQueryData(queryKeys.portfolioPosition(eventAccountKey(account), ticker ?? ""), position);
    },
    !!ticker,
  );

  useRealtime(
    "portfolio_update",
    ({ portfolio, account }) => {
      const position = portfolio.variable_income.find((p) => p.ticker === ticker);
      if (position) {
        queryClient.setQueryData(queryKeys.portfolioPosition(eventAccountKey(account), ticker ?? ""), position);
      }
    },
    !!ticker,
  );

  return query;
}
