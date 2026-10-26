import { keepPreviousData, useInfiniteQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type ApiError from "@/shared/lib/models/ApiError";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyLogFilter, StrategyLogPage } from "@/types";

/** Linhas por página; "Carregar mais" abre a seguinte na mesma tela. */
const STRATEGY_LOG_PAGE_SIZE = 6;

/** O registro da estratégia, da linha mais recente à mais antiga, uma página por vez. */
export function useStrategyLog(kind: StrategyLogFilter) {
  return useInfiniteQuery<
    StrategyLogPage,
    ApiError,
    StrategyLogPage[],
    ReturnType<typeof queryKeys.strategyLog>,
    number
  >({
    queryKey: queryKeys.strategyLog(kind),
    queryFn: ({ pageParam, signal }) => {
      const params = new URLSearchParams({ kind, offset: String(pageParam), limit: String(STRATEGY_LOG_PAGE_SIZE) });
      return apiFetch<StrategyLogPage>(`/api/strategies/me/log?${params}`, { signal });
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
