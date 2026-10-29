import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { News } from "@/types";

/** As manchetes da partida inteira, da mais nova para a mais antiga. */
export function useNews(simulationId: number) {
  const queryClient = useQueryClient();

  // A manchete nova chega pronta e vai para o topo; o id já presente deixa a lista como está
  useRealtime("news_published", (news) => {
    queryClient.setQueryData<News[]>(queryKeys.news(simulationId), (items) =>
      !items || items.some((item) => item.id === news.id) ? items : [news, ...items],
    );
  });

  return useQuery({
    queryKey: queryKeys.news(simulationId),
    queryFn: ({ signal }) => apiFetch<News[]>("/api/news", { signal }),
  });
}
