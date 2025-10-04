import { io, Socket } from "socket.io-client";

type Callback = (data: any) => void;

let socket: Socket | null = null;
const listeners: Map<string, Set<Callback>> = new Map();

export function startSocket(url = "/") {
  if (socket) return socket;
  socket = io(url, { autoConnect: true });

  socket.onAny((event: string, payload: any) => {
    const set = listeners.get(event);
    if (set) set.forEach((cb) => cb(payload));
  });

  socket.on("connect", () => {
    console.debug("[socketClient] connected", socket?.id);
  });

  socket.on("disconnect", (reason) => {
    console.debug("[socketClient] disconnected", reason);
  });

  return socket;
}

export function subscribe(event: string, cb: Callback) {
  if (!listeners.has(event)) listeners.set(event, new Set());
  listeners.get(event)!.add(cb);
  return () => listeners.get(event)!.delete(cb);
}

// helper to emit (if needed)
export function emit(event: string, payload?: any) {
  socket?.emit(event, payload);
}
