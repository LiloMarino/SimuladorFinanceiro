import { useInfiniteQuery, useQueryClient } from "@tanstack/react-query";
import type ApiError from "@/shared/lib/models/ApiError";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { News } from "@/types";
import { type Month, previousMonth } from "../../lib/months";
import { newsMonthOptions } from "./useNewsMonth";

/** As manchetes carregadas e os meses que já vieram, do mais novo ao mais antigo. */
type NewsHistory = { items: News[]; months: Month[] };

/**
 * O histórico do jornal, um mês por página: abre em `fromMonth` e a rolagem pede o mês anterior,
 * até o mês em que a partida começou.
 */
export function useNewsHistory(simulationId: number, startMonth: Month, fromMonth: Month) {
  const queryClient = useQueryClient();

  return useInfiniteQuery<News[], ApiError, NewsHistory, ReturnType<typeof queryKeys.newsHistory>, Month>({
    queryKey: queryKeys.newsHistory(simulationId, fromMonth),
    // Cada página é o cache do mês avulso: o mês carregado há pouco serve de página sem ir ao servidor
    queryFn: ({ pageParam }) => queryClient.query({ ...newsMonthOptions(simulationId, pageParam), staleTime: 30_000 }),
    initialPageParam: fromMonth,
    getNextPageParam: (_last, _pages, lastMonth) => {
      const previous = previousMonth(lastMonth);
      return previous >= startMonth ? previous : undefined;
    },
    select: (data) => ({ items: data.pages.flat(), months: data.pageParams }),
  });
}
