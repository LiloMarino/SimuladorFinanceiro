import type { QueryClient, QueryKey } from "@tanstack/react-query";

/**
 * Aplica o dado novo de um aviso do websocket na chave. A leitura HTTP em voo é cancelada
 * antes: uma resposta que saiu antes do aviso não chega depois dele e desfaz o que ele entregou.
 */
export async function applyRealtime<T>(client: QueryClient, queryKey: QueryKey, data: T): Promise<void> {
  await client.cancelQueries({ queryKey, exact: true });
  client.setQueryData<T>(queryKey, data);
}

/**
 * Aplica um aviso que acrescenta ao que a tela já tem (o ponto novo de uma série, os padrões
 * do último pregão, uma ordem do livro). `merge` devolve `null` quando o aviso não encaixa no
 * que a tela tem (um aviso se perdeu): a chave é lida de novo.
 * Sem dado base no cache não há onde acrescentar: uma leitura em voo é refeita, porque sua
 * resposta pode ter saído antes do aviso; sem leitura em voo a chave ainda não foi pedida.
 */
export async function applyRealtimeDelta<T>(
  client: QueryClient,
  queryKey: QueryKey,
  merge: (current: T) => T | null,
): Promise<void> {
  const current = client.getQueryData<T>(queryKey);
  if (current === undefined) {
    if (client.isFetching({ queryKey, exact: true }) > 0) {
      // A primeira leitura em voo só é refeita depois de cancelada
      await client.cancelQueries({ queryKey, exact: true });
      await client.invalidateQueries({ queryKey, exact: true });
    }
    return;
  }
  const next = merge(current);
  if (next === null) {
    await client.invalidateQueries({ queryKey, exact: true });
    return;
  }
  await client.cancelQueries({ queryKey, exact: true });
  // O merge roda sobre o cache já sem a leitura em voo, que o cancelamento pode ter revertido
  const base = client.getQueryData<T>(queryKey);
  client.setQueryData<T>(queryKey, base === undefined ? undefined : (merge(base) ?? base));
}
