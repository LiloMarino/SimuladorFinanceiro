import { createContext } from "react";
import type { BaseSubscriberRealtime } from "@/shared/lib/realtime/baseSubscriberRealtime";

export interface RealtimeContextValue<TEvents extends Record<string, unknown> = Record<string, unknown>> {
  subscriber: BaseSubscriberRealtime<TEvents>;
}

export const RealtimeContext = createContext<RealtimeContextValue | null>(null);
