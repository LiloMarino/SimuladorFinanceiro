import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { PortfolioState } from "@/types";

/**
 * Carteira do jogador (posições, caixa, histórico patrimonial), mantida viva
 * via snapshot_update (merge no histórico), fixed_income_position_update e
 * cash_update (patch de sub-campos).
 */
export function usePortfolio() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.portfolio(),
    queryFn: ({ signal }) => apiFetch<PortfolioState>("/api/portfolio", { signal }),
  });

  useRealtime("snapshot_update", ({ snapshot }) => {
    queryClient.setQueryData(queryKeys.portfolio(), (prev: PortfolioState | undefined) => {
      if (!prev) return prev;

      const map = new Map(prev.patrimonial_history.map((h) => [h.snapshot_date, h]));

      map.set(snapshot.snapshot_date, {
        snapshot_date: snapshot.snapshot_date,
        total_networth: String(snapshot.total_networth),
        total_equity: String(snapshot.total_equity),
        total_fixed: String(snapshot.total_fixed),
        total_cash: String(snapshot.total_cash),
        total_contribution: String(snapshot.total_contribution),
      });

      return {
        ...prev,
        patrimonial_history: Array.from(map.values()).sort((a, b) => a.snapshot_date.localeCompare(b.snapshot_date)),
      };
    });
  });

  useRealtime("fixed_income_position_update", (data) => {
    queryClient.setQueryData(queryKeys.portfolio(), (prev: PortfolioState | undefined) => {
      if (!prev) return prev;

      return {
        ...prev,
        fixed_income: data.positions,
      };
    });
  });

  useRealtime("cash_update", ({ cash }) => {
    queryClient.setQueryData(queryKeys.portfolio(), (prev: PortfolioState | undefined) => {
      if (!prev) return prev;

      return {
        ...prev,
        cash,
      };
    });
  });

  return query;
}
