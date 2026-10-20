import { keepPreviousData, useInfiniteQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type ApiError from "@/shared/lib/models/ApiError";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { LifeHistoryCategory, LifeHistoryPage } from "@/types";

/** Linhas por página; "Mostrar mais" abre a seguinte na mesma tela. */
export const LIFE_HISTORY_PAGE_SIZE = 6;

/**
 * O histórico da vida financeira, do mais recente ao mais antigo, uma página de cada vez
 * por deslocamento. Sem categoria, traz tudo. A anterior fica na tela enquanto o filtro troca.
 */
export function useLifeHistory(category: LifeHistoryCategory | null) {
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;

  return useInfiniteQuery<
    LifeHistoryPage,
    ApiError,
    LifeHistoryPage[],
    ReturnType<typeof queryKeys.lifeHistory>,
    number
  >({
    queryKey: queryKeys.lifeHistory(current?.id ?? 0, category ?? "ALL"),
    queryFn: ({ pageParam, signal }) => {
      const params = new URLSearchParams({
        offset: String(pageParam),
        limit: String(LIFE_HISTORY_PAGE_SIZE),
      });
      if (category) params.set("category", category);
      return apiFetch<LifeHistoryPage>(`/api/simulation/life-history?${params}`, { signal });
    },
    initialPageParam: 0,
    getNextPageParam: (last, pages) => {
      const loaded = pages.reduce((sum, page) => sum + page.items.length, 0);
      return loaded < last.total ? loaded : undefined;
    },
    select: (data) => data.pages,
    enabled: current?.game_type === "FINANCIAL_INDEPENDENCE",
    placeholderData: keepPreviousData,
  });
}
