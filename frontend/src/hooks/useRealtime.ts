import { useEffect } from "react";
import { useRealtimeContext } from "@/hooks/useRealtimeContext";
import type { SimulationEvents } from "@/types";

export function useRealtime<K extends keyof SimulationEvents>(event: K, callback: (data: SimulationEvents[K]) => void) {
  const { subscriber } = useRealtimeContext<SimulationEvents>();

  useEffect(() => {
    const unsubscribe = subscriber.subscribe(event, callback);
    return () => unsubscribe();
  }, [subscriber, event, callback]);
}
