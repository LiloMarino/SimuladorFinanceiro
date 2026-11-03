import type { News } from "@/types";

/** Quantas manchetes a edição de "Hoje" mostra: a grande e as três em colunas. */
const TODAY_SIZE = 4;

/**
 * As manchetes da edição do dia, da principal para as menores: ordem pela maior variação do preço
 * (para cima ou para baixo), com as sem variação (política, economia, história) depois, da mais nova
 * para a mais antiga. Cada ativo aparece uma vez, com a manchete de maior variação.
 */
export function pickToday(items: readonly News[]): News[] {
  const move = (item: News) => (item.change_pct === null ? -1 : Math.abs(item.change_pct));
  const byMove = [...items].sort((a, b) => move(b) - move(a));

  const seen = new Set<string>();
  const picked: News[] = [];
  for (const item of byMove) {
    if (item.tickers.some((ticker) => seen.has(ticker))) continue;
    item.tickers.forEach((ticker) => seen.add(ticker));
    picked.push(item);
    if (picked.length === TODAY_SIZE) break;
  }
  return picked;
}
