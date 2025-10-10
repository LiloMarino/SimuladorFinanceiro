import { io, Socket } from "socket.io-client";
import type { SubscriberRealtime } from "./subscriberRealtime";

export class SocketClient<TEvents extends Record<string, unknown> = Record<string, unknown>>
  implements SubscriberRealtime<TEvents>
{
  private socket: Socket | null = null;
  private listeners = new Map<keyof TEvents, Set<(data: TEvents[keyof TEvents]) => void>>();

  connect(url = "/realtime") {
    if (this.socket) return;
    this.socket = io(url, { autoConnect: true });

    this.socket.onAny((event, payload) => {
      this.listeners.get(event as keyof TEvents)?.forEach((cb) => cb(payload));
    });

    this.socket.on("connect", () => console.debug("[SocketClient] connected"));
    this.socket.on("disconnect", () => console.debug("[SocketClient] disconnected"));
  }

  subscribe<K extends keyof TEvents>(event: K, cb: (data: TEvents[K]) => void) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event)!.add(cb as (data: TEvents[keyof TEvents]) => void);
    return () => this.unsubscribe(event, cb);
  }

  unsubscribe<K extends keyof TEvents>(event: K, cb: (data: TEvents[K]) => void) {
    this.listeners.get(event)?.delete(cb as (data: TEvents[keyof TEvents]) => void);
  }

  emit<K extends keyof TEvents>(event: K, payload?: TEvents[K]) {
    this.socket?.emit(event as string, payload);
  }
}
