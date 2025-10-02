import { useEffect, useRef, useState } from "react";
import type { ZodType } from "zod";

interface UseStreamApiOptions<T> {
  onMessage?: (data: T) => void;
  onError?: (error: Event) => void;
  responseSchema?: ZodType<T>; // validação da resposta
}

export function useStreamApi<T = unknown>(
  url: string,
  options?: UseStreamApiOptions<T>
) {
  const [data, setData] = useState<T | null>(null);
  const [connected, setConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onopen = () => {
      setConnected(true);
    };

    es.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        const validated = options?.responseSchema
          ? options.responseSchema.parse(parsed)
          : (parsed as T);

        setData(validated);
        options?.onMessage?.(validated);
      } catch (err) {
        console.error("Erro ao processar SSE:", err);
      }
    };

    es.onerror = (err) => {
      setConnected(false);
      options?.onError?.(err);
      console.error("SSE error:", err);
      // se quiser encerrar ao erro
      // es.close();
    };

    return () => {
      es.close();
      setConnected(false);
    };
  }, [url, options]);

  return { data, connected, close: () => eventSourceRef.current?.close() };
}
