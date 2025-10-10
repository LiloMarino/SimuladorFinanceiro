import { useEffect } from "react";
import { useRealtimeContext } from "@/hooks/useRealtimeContext";

type RealtimeSubscriber<TEvents extends Record<string, unknown>> = {
  subscribe<K extends keyof TEvents>(event: K, callback: (data: TEvents[K]) => void): () => void;
};

export function useRealtime<TEvents extends Record<string, unknown>, K extends keyof TEvents>(
  event: K,
  callback: (data: TEvents[K]) => void
) {
  const { subscriber } = useRealtimeContext() as {
    subscriber: RealtimeSubscriber<TEvents>;
  };

  useEffect(() => {
    const unsubscribe = subscriber.subscribe(event, callback);
    return () => unsubscribe();
  }, [subscriber, event, callback]);
}
