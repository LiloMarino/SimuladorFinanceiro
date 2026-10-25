import { useEffect, useEffectEvent } from "react";
import { useRealtimeContext } from "@/shared/hooks/useRealtimeContext";
import { useAuth } from "@/shared/hooks/useAuth";
import type { SimulationEvents } from "@/types";

export function useRealtime<K extends keyof SimulationEvents>(
  event: K,
  callback: (data: SimulationEvents[K]) => void,
  enabled: boolean = true,
) {
  const { subscriber, connected } = useRealtimeContext<SimulationEvents>();
  const { session } = useAuth();
  const onEvent = useEffectEvent(callback);
  const isAuthenticated = session?.authenticated ?? false;

  useEffect(() => {
    if (!enabled) return;
    if (!isAuthenticated) return;
    if (!connected) return;

    const unsubscribe = subscriber.subscribe(event, (data) => {
      onEvent(data);
    });

    return () => {
      unsubscribe();
    };
  }, [subscriber, event, connected, isAuthenticated, enabled]);
}
