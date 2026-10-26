import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { Inbox } from "@/types";

/** As entradas do jogador e as da sala, da mais nova para a mais antiga, com quantas faltam ler. */
export function useInbox(simulationId: number) {
  const queryClient = useQueryClient();

  // A entrada nova chega pronta e vai para o topo; cada consumidor do hook recebe o
  // mesmo evento, e o id já presente deixa a lista como está
  useRealtime("inbox_entry", (entry) => {
    queryClient.setQueryData<Inbox>(queryKeys.inbox(simulationId), (inbox) =>
      !inbox || inbox.entries.some((e) => e.id === entry.id)
        ? inbox
        : { entries: [entry, ...inbox.entries], unread: inbox.unread + 1 },
    );
  });

  return useQuery({
    queryKey: queryKeys.inbox(simulationId),
    queryFn: ({ signal }) => apiFetch<Inbox>("/api/inbox", { signal }),
  });
}
