import { useEffect, useMemo, useState, type ReactNode } from "react";
import { SSEClient } from "@/shared/lib/realtime/SSEClient";
import { SocketClient } from "@/shared/lib/realtime/SocketClient";
import { RealtimeContext } from "./RealtimeContext";
import { useAuth } from "@/shared/hooks/useAuth";

type Mode = "sse" | "ws";

export function RealtimeProvider({ children, mode = "sse" }: { children: ReactNode; mode?: Mode }) {
  const [connected, setConnected] = useState(false);
  const { session, loading: authLoading } = useAuth();

  const subscriber = useMemo(() => {
    const instance = mode === "sse" ? new SSEClient() : new SocketClient();

    // Hooks simples de lifecycle
    instance.onConnect(() => {
      setConnected(true);
    });

    instance.onDisconnect(() => {
      setConnected(false);
    });

    return instance;
  }, [mode]);

  useEffect(() => {
    // Só conecta quando auth terminar E usuário estiver autenticado
    if (authLoading) return;
    if (!session?.authenticated) return;

    subscriber.connect();
  }, [authLoading, session?.authenticated, subscriber]);

  return <RealtimeContext.Provider value={{ subscriber, connected }}>{children}</RealtimeContext.Provider>;
}
