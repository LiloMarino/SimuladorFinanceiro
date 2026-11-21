import type { QueryClient } from "@tanstack/react-query";

/**
 * Depois de uma queda do socket, o que a tela mostra pode ter perdido avisos: toda leitura
 * anterior à queda é descartada, as ativas são lidas uma vez e as demais ficam marcadas para a próxima vez.
 */
export function refetchSinceDisconnect(client: QueryClient, lostAt: number): Promise<void> {
  return client.invalidateQueries({ predicate: (query) => query.state.dataUpdatedAt < lostAt });
}

/** Acompanha a conexão e diz, a cada mudança, quando é uma reconexão e desde quando o socket estava fora. */
export function createReconnectTracker(now: () => number = Date.now) {
  let everConnected = false;
  let lostAt: number | null = null;
  return (connected: boolean): number | null => {
    if (!connected) {
      if (everConnected && lostAt === null) lostAt = now();
      return null;
    }
    everConnected = true;
    const since = lostAt;
    lostAt = null;
    return since;
  };
}
