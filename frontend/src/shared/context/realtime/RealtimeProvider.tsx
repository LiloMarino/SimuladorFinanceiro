import { useMemo, type ReactNode } from "react";
import { SSEClient } from "@/shared/lib/realtime/sseClient";
import { SocketClient } from "@/shared/lib/realtime/socketClient";
import { RealtimeContext } from "./RealtimeContext";

type Mode = "sse" | "ws";

export function RealtimeProvider({ children, mode = "sse" }: { children: ReactNode; mode?: Mode }) {
  const subscriber = useMemo(() => {
    const instance = mode === "sse" ? new SSEClient() : new SocketClient();
    instance.connect();
    return instance;
  }, [mode]);

  return <RealtimeContext.Provider value={{ subscriber }}>{children}</RealtimeContext.Provider>;
}
