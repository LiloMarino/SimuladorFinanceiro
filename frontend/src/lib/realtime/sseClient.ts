type Callback = (data: any, ev?: MessageEvent) => void;

const listeners: Map<string, Set<Callback>> = new Map();
let es: EventSource | null = null;
let connected = false;
const STORAGE_KEY = "realtime_client_id";

export function startEventSource(url = "/api/stream") {
  if (es) return es;
  es = new EventSource(url);

  es.onopen = () => {
    connected = true;
    console.debug("[sseClient] connected");
  };

  es.onmessage = (ev) => {
    try {
      // Ev.data pode ser o blob {event, payload} ou server-sent event type
      const parsed = JSON.parse(ev.data);
      // If server sends {event, payload} inside data
      const type = parsed.event ?? parsed.type ?? "message";
      const payload = parsed.payload ?? parsed;

      // store client_id if it's the connected handshake
      if (type === "connected" && payload?.client_id) {
        try {
          localStorage.setItem(STORAGE_KEY, payload.client_id);
        } catch {
          /* ignore storage problems */
        }
      }

      const set = listeners.get(type);
      if (set) {
        set.forEach((cb) => cb(payload, ev));
      }
    } catch (err) {
      console.error("[sseClient] parse error", err);
    }
  };

  es.onerror = (ev) => {
    connected = false;
    console.error("[sseClient] error", ev);
    // ES automatic reconnect, no need to reopen
  };

  return es;
}

export function subscribe(eventType: string, cb: Callback) {
  if (!listeners.has(eventType)) listeners.set(eventType, new Set());
  listeners.get(eventType)!.add(cb);
  return () => {
    listeners.get(eventType)!.delete(cb);
  };
}

export function getClientId(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export async function updateSubscriptionOnServer(topics: string[]) {
  const client_id = getClientId();
  if (!client_id) return null;
  await fetch("/api/update-subscription", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id, topics }),
  });
}
