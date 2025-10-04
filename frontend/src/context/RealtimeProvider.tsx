import  { createContext, useContext, useEffect, type ReactNode } from "react";
import { startEventSource, updateSubscriptionOnServer, getClientId } from "@/lib/realtime/sseClient";
import { startSocket } from "@/lib/realtime/socketClient";

type Mode = "sse" | "ws";

interface RealtimeContextValue {
  mode: Mode;
  clientId: string | null;
  setTopics: (topics: string[]) => Promise<void>;
}

const RealtimeContext = createContext<RealtimeContextValue | null>(null);

export const useRealtime = () => {
  const c = useContext(RealtimeContext);
  if (!c) throw new Error("useRealtime must be used within RealtimeProvider");
  return c;
};

export function RealtimeProvider({ children, mode = "sse" as Mode }: { children: ReactNode; mode?: Mode }) {
  useEffect(() => {
    if (mode === "sse") {
      startEventSource("/api/stream");
    } else {
      startSocket();
    }
  }, [mode]);

  const clientId = getClientId();

  async function setTopics(topics: string[]) {
    if (mode === "sse") {
      await updateSubscriptionOnServer(topics);
    } else {
      // para WS, poderia emitir um evento para rooms / subscription
      // emit("subscribe", { topics });
    }
  }

  const value: RealtimeContextValue = {
    mode,
    clientId,
    setTopics,
  };

  return <RealtimeContext.Provider value={value}>{children}</RealtimeContext.Provider>;
}