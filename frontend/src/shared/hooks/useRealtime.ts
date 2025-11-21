import { useEffect, useRef } from "react";
import { useRealtimeContext } from "@/shared/hooks/useRealtimeContext";
import type { SimulationEvents } from "@/types";

export function useRealtime<K extends keyof SimulationEvents>(event: K, callback: (data: SimulationEvents[K]) => void) {
  const { subscriber } = useRealtimeContext<SimulationEvents>();
  const callbackRef = useRef(callback);

  // Atualiza a referência sempre que o callback mudar
  callbackRef.current = callback;

  useEffect(() => {
    const unsubscribe = subscriber.subscribe(event, (data: SimulationEvents[K]) => {
      callbackRef.current(data);
    });
    return () => unsubscribe();
  }, [subscriber, event]);
}
