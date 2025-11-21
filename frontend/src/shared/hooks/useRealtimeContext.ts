import { useContext } from "react";
import { RealtimeContext } from "@/shared/context/realtime";
import type { RealtimeContextValue } from "@/shared/context/realtime/RealtimeContext";

export function useRealtimeContext<TEvents extends Record<string, unknown>>() {
  const ctx = useContext(RealtimeContext) as RealtimeContextValue<TEvents> | null;
  if (!ctx) throw new Error("useRealtimeContext must be used within RealtimeProvider");
  return ctx;
}
