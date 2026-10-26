import { keepPreviousData, useInfiniteQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type ApiError from "@/shared/lib/models/ApiError";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyLogPage } from "@/types";

/** Linhas por página; "Carregar mais" abre a seguinte na mesma tela. */
const BOT_LOG_PAGE_SIZE = 6;

/** As ordens de um bot na partida, da mais recente à mais antiga, uma página por vez. */
export function useBotLog(simulationId: number, nickname: string) {
  return useInfiniteQuery<StrategyLogPage, ApiError, StrategyLogPage[], ReturnType<typeof queryKeys.botLog>, number>({
    queryKey: queryKeys.botLog(simulationId, nickname),
    queryFn: ({ pageParam, signal }) => {
      const params = new URLSearchParams({
        simulation_id: String(simulationId),
        nickname,
        offset: String(pageParam),
        limit: String(BOT_LOG_PAGE_SIZE),
      });
      return apiFetch<StrategyLogPage>(`/api/statistics/bots/log?${params}`, { signal });
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
