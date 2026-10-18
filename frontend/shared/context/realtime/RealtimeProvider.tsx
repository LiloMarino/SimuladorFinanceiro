import { useEffect, useMemo, useState, type ReactNode } from "react";
import { SocketClient } from "@/shared/lib/realtime/SocketClient";
import { RealtimeContext } from "./RealtimeContext";
import { useAuth } from "@/shared/hooks/useAuth";

export function RealtimeProvider({ children }: { children: ReactNode }) {
  const [connected, setConnected] = useState(false);
  const { session, loading: authLoading } = useAuth();

  const subscriber = useMemo(() => {
    const instance = new SocketClient();

    // Hooks simples de lifecycle
    instance.onConnect(() => {
      setConnected(true);
    });

    instance.onDisconnect(() => {
      setConnected(false);
    });

    return instance;
  }, []);

  useEffect(() => {
    // Só conecta quando auth terminar E usuário estiver autenticado
    if (authLoading) return;
    if (!session?.authenticated) return;

    subscriber.connect();
  }, [authLoading, session?.authenticated, subscriber]);

  return <RealtimeContext.Provider value={{ subscriber, connected }}>{children}</RealtimeContext.Provider>;
}
