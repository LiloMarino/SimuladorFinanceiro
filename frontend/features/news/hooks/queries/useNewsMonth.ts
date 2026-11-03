import { type InfiniteData, queryOptions, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { News } from "@/types";
import { type Month, monthOf } from "../../lib/months";

/** As manchetes de um mês, da mais nova para a mais antiga; o histórico lê as páginas por aqui. */
export function newsMonthOptions(simulationId: number, month: Month) {
  return queryOptions({
    queryKey: queryKeys.newsMonth(simulationId, month),
    queryFn: ({ signal }) => apiFetch<News[]>(`/api/news?${new URLSearchParams({ month })}`, { signal }),
  });
}

/** As manchetes de um mês; a manchete nova do pregão entra sozinha no mês dela. */
export function useNewsMonth(simulationId: number, month: Month) {
  const queryClient = useQueryClient();

  // A manchete nova chega pronta e vai para o topo do mês dela, no mês avulso e na página do histórico;
  // o id já presente deixa a lista como está
  useRealtime("news_published", (news) => {
    const publishedMonth = monthOf(news.news_date);
    queryClient.setQueryData<News[]>(queryKeys.newsMonth(simulationId, publishedMonth), (items) =>
      !items || items.some((item) => item.id === news.id) ? items : [news, ...items],
    );
    queryClient.setQueriesData<InfiniteData<News[], Month>>(
      { queryKey: queryKeys.newsHistory(simulationId) },
      (history) => {
        const index = history?.pageParams.indexOf(publishedMonth) ?? -1;
        if (!history || index < 0 || history.pages[index]?.some((item) => item.id === news.id)) return history;
        return { ...history, pages: history.pages.map((page, i) => (i === index ? [news, ...page] : page)) };
      },
    );
  });

  return useQuery(newsMonthOptions(simulationId, month));
}
