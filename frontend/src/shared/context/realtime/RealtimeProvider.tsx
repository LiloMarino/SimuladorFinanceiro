import { useMemo, useState, type ReactNode } from "react";
import { SSEClient } from "@/shared/lib/realtime/sseClient";
import { SocketClient } from "@/shared/lib/realtime/socketClient";
import { RealtimeContext } from "./RealtimeContext";

type Mode = "sse" | "ws";

export function RealtimeProvider({ children, mode = "sse" }: { children: ReactNode; mode?: Mode }) {
  const [connected, setConnected] = useState(false);

  const subscriber = useMemo(() => {
    const instance = mode === "sse" ? new SSEClient() : new SocketClient();

    // Hooks simples de lifecycle
    instance.onConnect(() => {
      setConnected(true);
    });

    instance.onDisconnect(() => {
      setConnected(false);
    });

    instance.connect();
    return instance;
  }, [mode]);

  return <RealtimeContext.Provider value={{ subscriber, connected }}>{children}</RealtimeContext.Provider>;
}
