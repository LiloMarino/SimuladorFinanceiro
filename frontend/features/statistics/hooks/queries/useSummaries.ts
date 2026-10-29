import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Summary } from "@/types";

/** Os resumos do mês e as retrospectivas do ano do jogador, do mais novo para o mais antigo. */
export function useSummaries(simulationId: number) {
  const queryClient = useQueryClient();

  // O resumo novo chega pronto e vai para o topo; o id já presente deixa a lista como está
  useRealtime("summary_delivered", (summary) => {
    queryClient.setQueryData<Summary[]>(queryKeys.summaries(simulationId), (summaries) =>
      !summaries || summaries.some((s) => s.id === summary.id) ? summaries : [summary, ...summaries],
    );
  });

  return useQuery({
    queryKey: queryKeys.summaries(simulationId),
    queryFn: ({ signal }) => apiFetch<Summary[]>("/api/summaries", { signal }),
  });
}
