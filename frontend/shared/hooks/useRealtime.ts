import { useEffect, useRef } from "react";
import { useRealtimeContext } from "@/shared/hooks/useRealtimeContext";
import { useAuth } from "@/shared/hooks/useAuth";
import type { SimulationEvents } from "@/types";

export function useRealtime<K extends keyof SimulationEvents>(
  event: K,
  callback: (data: SimulationEvents[K]) => void,
  enabled: boolean = true
) {
  const { subscriber, connected } = useRealtimeContext<SimulationEvents>();
  const { session } = useAuth();
  const callbackRef = useRef(callback);
  const isAuthenticated = session?.authenticated ?? false;

  callbackRef.current = callback;

  useEffect(() => {
    if (!enabled) return;
    if (!isAuthenticated) return;
    if (!connected) return;

    const unsubscribe = subscriber.subscribe(event, (data) => {
      callbackRef.current(data);
    });

    return () => {
      unsubscribe();
    };
  }, [subscriber, event, connected, isAuthenticated, enabled]);
}
