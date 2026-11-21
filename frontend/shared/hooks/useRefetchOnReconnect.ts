import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useRealtimeContext } from "@/shared/hooks/useRealtimeContext";
import { createReconnectTracker, refetchSinceDisconnect } from "@/shared/lib/realtime/refetch-on-reconnect";

/** A cada reconexão do socket, as leituras ativas anteriores à queda são lidas uma vez; a primeira conexão não dispara nada. */
export function useRefetchOnReconnect() {
  const queryClient = useQueryClient();
  const { connected } = useRealtimeContext();
  const tracker = useRef(createReconnectTracker());

  useEffect(() => {
    const lostAt = tracker.current(connected);
    if (lostAt !== null) void refetchSinceDisconnect(queryClient, lostAt);
  }, [connected, queryClient]);
}
