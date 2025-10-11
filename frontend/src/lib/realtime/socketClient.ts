import { io, type Socket } from "socket.io-client";
import { BaseSubscriberRealtime } from "./baseSubscriberRealtime";

export class SocketClient<
  TEvents extends Record<string, unknown> = Record<string, unknown>
> extends BaseSubscriberRealtime<TEvents> {
  private socket: Socket | null = null;

  connect(url?: string) {
    const baseUrl = url || (typeof window !== "undefined" ? window.location.origin : "http://localhost:5173");

    console.log(baseUrl);
    if (this.socket) return;

    this.socket = io(baseUrl, { autoConnect: true, path: "/socket.io", transports: ["websocket"] });

    this.socket.onAny((event: string, payload: unknown) => {
      console.info("[SocketClient] event", event, payload);
      this.notify(event as keyof TEvents, payload as TEvents[keyof TEvents]);
    });

    this.socket.on("connect", () => console.info("[SocketClient] connected"));
    this.socket.on("disconnect", () => console.info("[SocketClient] disconnected"));

    this.socket.on("subscribed", (payload) => {
      console.info("[SocketClient] subscription confirmed", payload);
    });
  }

  protected async updateBackendSubscription(): Promise<void> {
    if (!this.socket) return;
    const events = Array.from(this.listeners.keys());
    this.socket.emit("subscribe", { events });
  }
}
