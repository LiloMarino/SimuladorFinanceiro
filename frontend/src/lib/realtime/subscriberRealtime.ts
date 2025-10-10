/**
 * Define o formato dos eventos possíveis, ex:
 * type MyEvents = { price_update: PriceData; user_joined: UserData }
 */
export interface SubscriberRealtime<TEvents extends Record<string, unknown> = Record<string, unknown>> {
  connect(): void;

  subscribe<K extends keyof TEvents>(event: K, cb: (data: TEvents[K]) => void): () => void;

  unsubscribe<K extends keyof TEvents>(event: K, cb: (data: TEvents[K]) => void): void;

  emit?<K extends keyof TEvents>(event: K, payload?: TEvents[K]): void;
}
