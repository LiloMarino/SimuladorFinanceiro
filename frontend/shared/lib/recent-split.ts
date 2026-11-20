/** Quantos itens o seletor mostra por inteiro; acima disso ficam os 3 mais recentes e o "Anteriores". */
const ITEMS_IN_ROW = 4;
const RECENT_ITEMS = 3;

export type RecentSplit<T> = {
  /** Os itens que ficam no seletor, do mais antigo ao mais recente. */
  row: T[];
  /** Os que ficam atrás do "Anteriores"; vazio com até 4 itens. */
  older: T[];
};

/** Separa a lista (do mais antigo ao mais recente) entre os itens à vista e os que ficam atrás do "Anteriores". */
export function splitRecent<T>(items: T[]): RecentSplit<T> {
  if (items.length <= ITEMS_IN_ROW) return { row: items, older: [] };
  return { row: items.slice(-RECENT_ITEMS), older: items.slice(0, -RECENT_ITEMS) };
}
