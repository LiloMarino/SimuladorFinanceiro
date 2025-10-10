import { useContext } from "react";
import { RealtimeContext } from "@/context/realtime";

export function useRealtimeContext() {
  const ctx = useContext(RealtimeContext);
  if (!ctx) throw new Error("useRealtimeContext must be used within RealtimeProvider");
  return ctx;
}
