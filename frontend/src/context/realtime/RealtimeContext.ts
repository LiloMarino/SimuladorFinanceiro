import { createContext } from "react";
import type { SubscriberRealtime } from "@/lib/realtime/subscriberRealtime";

export interface RealtimeContextValue {
  subscriber: SubscriberRealtime;
}
export const RealtimeContext = createContext<RealtimeContextValue | null>(null);
