import { keepPreviousData, useInfiniteQuery } from "@tanstack/react-query";
import { useStrategyRoute } from "@/shared/hooks/useStrategyRoute";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type ApiError from "@/shared/lib/models/ApiError";
import { queryKeys } from "@/shared/lib/queryKeys";
import { strategyFundId, strategyPaths } from "@/shared/lib/strategy-route";
import type { StrategyLogFilter, StrategyLogPage } from "@/types";

/** Linhas por página; a rolagem pede a seguinte sozinha. */
const STRATEGY_LOG_PAGE_SIZE = 6;

/**
 * O registro da estratégia da conta do topo, da linha mais recente à mais antiga, uma página por vez. Cada
 * página parte do id da última linha da anterior, então as linhas novas que chegam por `strategy_log_update`
 * não repetem nem pulam nenhuma.
 */
export function useStrategyLog(kind: StrategyLogFilter) {
  const fundId = strategyFundId(useStrategyRoute());

  return useInfiniteQuery<
    StrategyLogPage,
    ApiError,
    StrategyLogPage[],
    ReturnType<typeof queryKeys.strategyLog>,
    number | null
  >({
    queryKey: queryKeys.strategyLog(fundId ?? "personal", kind),
    queryFn: ({ pageParam, signal }) => {
      const params = new URLSearchParams({ kind, limit: String(STRATEGY_LOG_PAGE_SIZE) });
      if (pageParam !== null) params.set("before", String(pageParam));
      return apiFetch<StrategyLogPage>(`${strategyPaths(fundId).log}?${params}`, { signal });
    },
    initialPageParam: null,
    getNextPageParam: (last, pages) => {
      const loaded = pages.reduce((sum, page) => sum + page.items.length, 0);
      return loaded < last.total ? (last.items.at(-1)?.id ?? undefined) : undefined;
    },
    select: (data) => data.pages,
    placeholderData: keepPreviousData,
  });
}
