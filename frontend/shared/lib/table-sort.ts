export type SortValue = string | number | null | undefined;
export type SortDirection = "asc" | "desc";
export type TableSort<K extends string = string> = { column: K; direction: SortDirection };
export type SortColumns<T, K extends string = string> = Record<K, (row: T) => SortValue>;

const collator = new Intl.Collator("pt-BR", { numeric: true, sensitivity: "base" });
const missing = (value: SortValue) => value == null || (typeof value === "number" && !Number.isFinite(value));

/** Valores ausentes ficam no fim nos dois sentidos; empates preservam a ordem recebida. */
export function sortTableRows<T, K extends string>(
  rows: readonly T[],
  columns: SortColumns<T, K>,
  sort: TableSort<K> | null,
): T[] {
  if (!sort) return [...rows];
  const value = columns[sort.column];
  if (!value) return [...rows];
  return rows
    .map((row) => ({ row, value: value(row) }))
    .sort((a, b) => {
      const left = a.value;
      const right = b.value;
      if (missing(left)) return missing(right) ? 0 : 1;
      if (missing(right)) return -1;
      const compared =
        typeof left === "number" && typeof right === "number"
          ? left - right
          : collator.compare(String(left), String(right));
      return sort.direction === "asc" ? compared : -compared;
    })
    .map((entry) => entry.row);
}

export function nextTableSort<K extends string>(current: TableSort<K> | null, column: K): TableSort<K> {
  return { column, direction: current?.column === column && current.direction === "asc" ? "desc" : "asc" };
}

/** Decimal opcional recebido da API; zero é um valor válido. */
export const sortNumber = (value: string | number | null | undefined): number | null =>
  value == null ? null : Number(value);
