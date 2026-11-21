import { keepPreviousData, useInfiniteQuery } from "@tanstack/react-query";
import { useStrategyRoute } from "@/shared/hooks/useStrategyRoute";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type ApiError from "@/shared/lib/models/ApiError";
import { queryKeys } from "@/shared/lib/queryKeys";
import { strategyFundId, strategyPaths } from "@/shared/lib/strategy-route";
import type { StrategyLogFilter, StrategyLogPage } from "@/types";

/** Linhas por página; a rolagem pede a seguinte sozinha. */
const STRATEGY_LOG_PAGE_SIZE = 6;

/** O registro da estratégia da conta do topo, da linha mais recente à mais antiga, uma página por vez. */
export function useStrategyLog(kind: StrategyLogFilter) {
  const fundId = strategyFundId(useStrategyRoute());

  return useInfiniteQuery<
    StrategyLogPage,
    ApiError,
    StrategyLogPage[],
    ReturnType<typeof queryKeys.strategyLog>,
    number
  >({
    queryKey: queryKeys.strategyLog(fundId ?? "personal", kind),
    queryFn: ({ pageParam, signal }) => {
      const params = new URLSearchParams({ kind, offset: String(pageParam), limit: String(STRATEGY_LOG_PAGE_SIZE) });
      return apiFetch<StrategyLogPage>(`${strategyPaths(fundId).log}?${params}`, { signal });
    },
    initialPageParam: 0,
    getNextPageParam: (last, pages) => {
      const loaded = pages.reduce((sum, page) => sum + page.items.length, 0);
      return loaded < last.total ? loaded : undefined;
    },
    select: (data) => data.pages,
    placeholderData: keepPreviousData,
  });
}
