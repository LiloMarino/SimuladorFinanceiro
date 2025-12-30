import { useEffect, useRef } from "react";
import { useRealtimeContext } from "@/shared/hooks/useRealtimeContext";
import { useAuth } from "@/shared/hooks/useAuth";
import type { SimulationEvents } from "@/types";

export function useRealtime<K extends keyof SimulationEvents>(event: K, callback: (data: SimulationEvents[K]) => void) {
  const { subscriber, connected } = useRealtimeContext<SimulationEvents>();
  const { getSession } = useAuth();
  const session = getSession();
  const callbackRef = useRef(callback);

  // Atualiza a referência sempre que o callback mudar
  callbackRef.current = callback;

  useEffect(() => {
    if (!session?.authenticated) return;
    if (!connected) return;

    const unsubscribe = subscriber.subscribe(event, (data) => {
      callbackRef.current(data);
    });

    return () => {
      unsubscribe();
    };
  }, [subscriber, event, connected, session]);
}
