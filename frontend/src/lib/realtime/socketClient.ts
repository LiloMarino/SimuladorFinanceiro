import { io, type Socket } from "socket.io-client";
import { BaseSubscriberRealtime } from "./baseSubscriberRealtime";

export class SocketClient<
  TEvents extends Record<string, unknown> = Record<string, unknown>
> extends BaseSubscriberRealtime<TEvents> {
  private socket: Socket | null = null;

  connect(url = "http://localhost:5000") {
    if (this.socket) return;
    this.socket = io(url, { autoConnect: true, path: "/socket.io" });

    this.socket.onAny((event: string, payload: unknown) => {
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
