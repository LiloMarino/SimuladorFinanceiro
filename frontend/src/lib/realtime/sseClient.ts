import { BaseSubscriberRealtime } from "./baseSubscriberRealtime";

export class SSEClient<
  TEvents extends Record<string, unknown> = Record<string, unknown>
> extends BaseSubscriberRealtime<TEvents> {
  private es: EventSource | null = null;

  connect(url = "/api/stream") {
    if (this.es) return;
    this.es = new EventSource(url);

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

    this.es.onerror = (err) => console.error("[SSEClient] error", err);
  }
}
