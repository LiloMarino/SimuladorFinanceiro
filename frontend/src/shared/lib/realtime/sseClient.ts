import { BaseSubscriberRealtime } from "./baseSubscriberRealtime";

export class SSEClient<
  TEvents extends Record<string, unknown> = Record<string, unknown>
> extends BaseSubscriberRealtime<TEvents> {
  private es: EventSource | null = null;

  connect(url = "/api/stream") {
    if (this.es) return;

    // Passa o clientId como query string
    this.es = new EventSource(url);

    this.es.onopen = () => {
      console.debug("[SSEClient] connected");
      this.setConnected(true);
    };

    this.es.onmessage = (ev) => {
      try {
        const parsed = JSON.parse(ev.data);
        const type = parsed.event ?? "message";
        const payload = parsed.payload ?? parsed;
        this.notify(type as keyof TEvents, payload as TEvents[keyof TEvents]);
      } catch (err) {
        console.error("[SSEClient] parse error", err);
      }
    };

    this.es.onerror = (err) => {
      console.error("[SSEClient] error", err);
      this.setConnected(false);
    };
  }

  protected async updateBackendSubscription(): Promise<void> {
    const events = Array.from(this.listeners.keys());
    try {
      await fetch("/api/update-subscription", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events }),
        credentials: "include",
      });
    } catch (err) {
      console.error("[SSEClient] failed to update subscription", err);
    }
  }
}
