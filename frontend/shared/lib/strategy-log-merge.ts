import type { InfiniteData } from "@tanstack/react-query";
import type { StrategyLogFilter, StrategyLogPage, StrategyLogRow } from "@/types";

/** O registro no cache: uma página por vez, cada uma pedida pelo id da última linha da anterior (a primeira, sem id). */
export type StrategyLogData = InfiniteData<StrategyLogPage, number | null>;

const matchesFilter = (row: StrategyLogRow, filter: StrategyLogFilter) =>
  row.kind !== "error_seen" && (filter === "all" || (filter === "orders") === (row.kind === "order"));

// A ordem do registro: o dia e, no mesmo dia, a linha gravada por último, primeiro
const isNewer = (a: StrategyLogRow, b: StrategyLogRow) =>
  a.event_date !== b.event_date ? a.event_date > b.event_date : a.id > b.id;

/**
 * Aplica um aviso do registro (linhas novas ou mudadas e o total do filtro) ao que a tela já carregou:
 * a linha nova entra no topo da primeira página, a linha mudada troca a que tem o mesmo id, e o total
 * passa a ser o do servidor. Uma linha mudada que a tela ainda não carregou fica para quando a página
 * dela chegar. Devolve `null` quando o aviso não encaixa (o total cresceu além das linhas novas que
 * chegaram: um aviso se perdeu), e a tela lê o registro de novo.
 */
export function mergeStrategyLog(
  data: StrategyLogData,
  filter: StrategyLogFilter,
  rows: StrategyLogRow[],
  total: number,
): StrategyLogData | null {
  const [first] = data.pages;
  if (first === undefined) return null;

  const previousTotal = first.total;
  const loaded = data.pages.reduce((sum, page) => sum + page.items.length, 0);
  const known = new Set(data.pages.flatMap((page) => page.items.map((row) => row.id)));
  const matching = rows.filter((row) => matchesFilter(row, filter));
  const changed = new Map(matching.filter((row) => known.has(row.id)).map((row) => [row.id, row]));

  // As linhas desconhecidas só entram quando são mais novas que o topo; as mais velhas são mudanças fora da tela
  const top = first.items[0];
  const added = matching
    .filter((row) => !known.has(row.id) && (top === undefined || isNewer(row, top)))
    .sort((a, b) => (isNewer(a, b) ? -1 : 1));

  if (total - previousTotal !== added.length || loaded + added.length > total) return null;

  const replace = (page: StrategyLogPage, index: number): StrategyLogPage => ({
    total,
    items: [...(index === 0 ? added : []), ...page.items.map((row) => changed.get(row.id) ?? row)],
  });
  return { ...data, pages: data.pages.map(replace) };
}
