import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Inbox, InboxEntry } from "@/types";

/** Marca a entrada aberta como lida; a lista e o contador mudam na hora. */
export function useMarkInboxEntryRead(simulationId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (entryId: InboxEntry["id"]) =>
      apiFetch<void>(`/api/inbox/${entryId}/read`, { method: "POST", body: {} }),
    onSuccess: (_, entryId) => {
      queryClient.setQueryData<Inbox>(
        queryKeys.inbox(simulationId),
        (inbox) =>
          inbox && {
            entries: inbox.entries.map((e) => (e.id === entryId ? { ...e, read: true } : e)),
            unread: Math.max(inbox.unread - 1, 0),
          },
      );
    },
  });
}
