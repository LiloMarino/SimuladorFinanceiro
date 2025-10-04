import { useEffect, useRef, useState, useCallback } from "react";
import type { ZodType } from "zod";

interface UseSocketApiOptions<T = unknown> {
  onMessage?: (data: T, event?: MessageEvent) => void;
  onError?: (error: Event) => void;
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  responseSchema?: ZodType<T>;
  reconnect?: boolean;
  reconnectDelayMs?: number;
}

export function useSocketApi<T = unknown>(url: string, options?: UseSocketApiOptions<T>) {
  const [data, setData] = useState<T | null>(null);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<number | null>(null);

  const cleanup = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }
    socketRef.current?.close();
  }, []);

  const connect = useCallback(() => {
    const ws = new WebSocket(url);
    socketRef.current = ws;

    ws.onopen = (event) => {
      setConnected(true);
      options?.onOpen?.(event);
    };

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        const validated = options?.responseSchema
          ? options.responseSchema.parse(parsed)
          : (parsed as T);
        setData(validated);
        options?.onMessage?.(validated, event);
      } catch (err) {
        console.error("Erro ao processar WebSocket:", err);
      }
    };

    ws.onerror = (err) => {
      options?.onError?.(err);
      console.error("WebSocket error:", err);
    };

    ws.onclose = (event) => {
      setConnected(false);
      options?.onClose?.(event);

      if (options?.reconnect) {
        reconnectTimer.current = window.setTimeout(
          connect,
          options.reconnectDelayMs ?? 3000
        );
      }
    };
  }, [url, options]);

  useEffect(() => {
    connect();
    return () => cleanup();
  }, [connect, cleanup]);

  const send = (message: unknown) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn("WebSocket não está conectado. Mensagem ignorada:", message);
      return;
    }
    socketRef.current.send(JSON.stringify(message));
  };

  return { data, connected, send, close: cleanup };
}
