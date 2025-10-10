import type { SubscriberRealtime } from "./subscriberRealtime";

export class SSEClient<TEvents extends Record<string, unknown> = Record<string, unknown>>
  implements SubscriberRealtime<TEvents>
{
  private es: EventSource | null = null;
  private listeners = new Map<keyof TEvents, Set<(data: TEvents[keyof TEvents]) => void>>();

  connect(url = "/api/stream") {
    if (this.es) return;
    this.es = new EventSource(url);

    this.es.onmessage = (ev) => {
      try {
        const parsed = JSON.parse(ev.data);
        const type = parsed.event ?? "message";
        const payload = parsed.payload ?? parsed;
        this.listeners.get(type as keyof TEvents)?.forEach((cb) => cb(payload));
      } catch (err) {
        console.error("[SSEClient] parse error", err);
      }
    };

    this.es.onerror = (err) => {
      console.error("[SSEClient] error", err);
    };
  }

  subscribe<K extends keyof TEvents>(event: K, cb: (data: TEvents[K]) => void) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event)!.add(cb as (data: TEvents[keyof TEvents]) => void);
    return () => this.unsubscribe(event, cb);
  }

  unsubscribe<K extends keyof TEvents>(event: K, cb: (data: TEvents[K]) => void) {
    this.listeners.get(event)?.delete(cb as (data: TEvents[keyof TEvents]) => void);
  }
}
